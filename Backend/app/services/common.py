from typing import List, Type, Dict, Any
from sqlmodel import SQLModel, Session, select, func
from fastapi import HTTPException


class CommonService:
    @staticmethod
    def paginate_query(
        session: Session, model: Type[SQLModel], page: int = 1, page_size: int = 20
    ) -> tuple[List[SQLModel], int, int]:
        """通用分页查询（动态主键支持）"""
        if page < 1 or page_size < 1:
            raise HTTPException(
                status_code=400, detail="Page and page_size must be positive"
            )

        offset = (page - 1) * page_size
        items = session.exec(select(model).offset(offset).limit(page_size)).all()

        # 🔑 动态获取主键列
        pk_cols = model.__table__.primary_key.columns
        if not pk_cols:
            raise RuntimeError(f"Model {model.__name__} has no primary key")
        pk_col = list(pk_cols)[0]
        total = session.exec(select(func.count(pk_col))).one()

        total_pages = (total + page_size - 1) // page_size
        return items, total, total_pages

    @staticmethod
    def get_by_id(
        session: Session, model: Type[SQLModel], id_value: int, id_field: str
    ):
        """根据ID获取对象"""
        field = getattr(model, id_field)
        stmt = select(model).where(field == id_value)
        obj = session.exec(stmt).first()
        if not obj:
            raise HTTPException(
                404, f"{model.__name__} with {id_field}={id_value} not found"
            )
        return obj

    @staticmethod
    def inject_relations(
        session: Session,
        items: List[SQLModel],
        relation_map: Dict[
            str, tuple
        ],  # field -> (model, pk_attr_name, target_attr, alias)
    ) -> List[dict]:
        """注入关联数据"""
        item_dicts = [item.model_dump() for item in items]

        # 收集各模型需查询的 ID
        id_map: Dict[type, set] = {}
        for field, (rel_model, pk_attr_name, _, _) in relation_map.items():
            ids = {d[field] for d in item_dicts if d.get(field) is not None}
            if ids:
                id_map[rel_model] = id_map.get(rel_model, set()) | ids

        # 批量查询并缓存
        cache: Dict[type, Dict[Any, Any]] = {}
        for rel_model, ids in id_map.items():
            # 找到这个模型对应的第一个relation配置
            relation_key = [k for k in relation_map if relation_map[k][0] == rel_model][
                0
            ]
            pk_attr_name = relation_map[relation_key][1]  # 获取主键属性名

            pk_attr = getattr(rel_model, pk_attr_name)  # 获取主键属性
            stmt = select(rel_model).where(pk_attr.in_(ids))
            objs = session.exec(stmt).all()
            cache[rel_model] = {getattr(obj, pk_attr_name): obj for obj in objs}

        # 注入字段
        for d in item_dicts:
            for field, (
                rel_model,
                pk_attr_name,
                target_attr,
                alias,
            ) in relation_map.items():
                rid = d.get(field)
                if rid is not None and rel_model in cache and rid in cache[rel_model]:
                    obj = cache[rel_model][rid]
                    d[alias] = getattr(obj, target_attr, None)
                else:
                    d[alias] = None

        return item_dicts
