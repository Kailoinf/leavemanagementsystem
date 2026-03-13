"""数据导出API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from fastapi.responses import StreamingResponse
from datetime import datetime

from app.database.connection import get_session
from app.services.export import ExportService
from app.services.leave import LeaveService
from app.api.deps import check_login
from sqlmodel import select
from app.models import Leave

router = APIRouter()


@router.get("/export/leaves/csv")
async def export_leaves_csv(
    token: str,
    session: Session = Depends(get_session),
):
    """导出请假记录为CSV格式"""
    # 验证登录状态
    obj = check_login(token, session)

    # 获取请假数据
    leaves_data = LeaveService.get_leaves_by_student(token, obj["id"], session)
    if obj["role"] != "student":
        # 如果不是学生，获取所有可见的请假记录
        items, _, _ = LeaveService.get_leaves(token, 1, 10000, session)
        leaves_data = items

    # 转换为字典格式
    export_data = []
    for leave in leaves_data:
        export_data.append({
            "请假编号": leave.get("leave_id"),
            "学生姓名": leave.get("student_name", "未知"),
            "请假日期": leave.get("leave_date", "").replace("T", " ") if leave.get("leave_date") else "",
            "请假天数": leave.get("leave_days"),
            "请假类型": leave.get("leave_type", ""),
            "状态": leave.get("status"),
            "审核员": leave.get("reviewer_name", ""),
            "审核时间": leave.get("audit_time", "").replace("T", " ") if leave.get("audit_time") else "",
            "备注": leave.get("remarks", ""),
        })

    # 生成CSV
    try:
        csv_data = ExportService.export_to_csv(export_data, "leaves")
        filename = ExportService.generate_filename("leaves", "csv")

        return StreamingResponse(
            csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/leaves/json")
async def export_leaves_json(
    token: str,
    session: Session = Depends(get_session),
):
    """导出请假记录为JSON格式"""
    # 验证登录状态
    obj = check_login(token, session)

    # 获取请假数据
    leaves_data = LeaveService.get_leaves_by_student(token, obj["id"], session)
    if obj["role"] != "student":
        # 如果不是学生，获取所有可见的请假记录
        items, _, _ = LeaveService.get_leaves(token, 1, 10000, session)
        leaves_data = items

    # 生成JSON
    try:
        json_data = ExportService.export_to_json(leaves_data, "leaves")
        filename = ExportService.generate_filename("leaves", "json")

        return StreamingResponse(
            json_data,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/leaves/excel")
async def export_leaves_excel(
    token: str,
    session: Session = Depends(get_session),
):
    """导出请假记录为Excel格式"""
    # 验证登录状态
    obj = check_login(token, session)

    # 获取请假数据
    leaves = []
    if obj["role"] == "student":
        # 学生获取自己的请假记录
        leaves_data = LeaveService.get_leaves_by_student(token, obj["id"], session)
        # 转换为Leave对象
        student_ids = {item.get("student_id") for item in leaves_data if item.get("student_id")}
        if student_ids:
            leaves = session.exec(
                select(Leave).where(Leave.student_id.in_(student_ids))
            ).all()
    else:
        # 其他角色获取所有可见的请假记录
        items, _, _ = LeaveService.get_leaves(token, 1, 10000, session)
        leave_ids = {item.get("leave_id") for item in items if item.get("leave_id")}
        if leave_ids:
            leaves = session.exec(
                select(Leave).where(Leave.leave_id.in_(leave_ids))
            ).all()

    # 生成Excel
    try:
        excel_data = ExportService.export_leaves_to_excel(leaves, session)
        filename = ExportService.generate_filename("leaves", "xlsx")

        return StreamingResponse(
            excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ImportError as e:
        raise HTTPException(status_code=500, detail="Excel导出功能需要安装openpyxl包")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
