/**
 * Excel 导出工具函数
 */
import * as XLSX from 'xlsx'

/**
 * 将数据导出为 Excel 文件并下载
 * @param data 要导出的数据数组
 * @param filename 文件名（不包含扩展名）
 * @param headers Excel 列名数组，如果为空则使用对象的键
 */
export const exportToExcel = (data: any[], filename: string, headers?: string[]) => {
  if (!data || data.length === 0) {
    console.warn('没有数据可以导出')
    return
  }

  // 获取列名
  let excelHeaders: string[]
  if (headers && headers.length > 0) {
    excelHeaders = headers
  } else {
    // 如果没有提供 headers，使用对象的键
    excelHeaders = Object.keys(data[0])
  }

  // 准备工作表数据
  const worksheetData = []

  // 添加表头
  worksheetData.push(excelHeaders)

  // 添加数据行
  data.forEach(row => {
    const values = excelHeaders.map(header => {
      // 获取对应的值
      const value = row[header]
      // 如果值为 null 或 undefined，返回空字符串
      if (value === null || value === undefined) {
        return ''
      }
      return value
    })
    worksheetData.push(values)
  })

  // 创建工作表
  const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)

  // 设置列宽
  const columnWidths = excelHeaders.map((header, index) => {
    // 计算该列的最大宽度
    let maxLength = header.length
    data.forEach(row => {
      const value = row[header] || ''
      const length = String(value).length
      if (length > maxLength) {
        maxLength = length
      }
    })
    // 设置最小宽度为10，最大宽度为50
    const width = Math.max(10, Math.min(50, maxLength + 2))
    return { width: width }
  })
  worksheet['!cols'] = columnWidths

  // 创建工作簿
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '数据')

  // 生成文件名（包含时间戳）
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  const fullFilename = `${filename}_${timestamp}.xlsx`

  // 导出文件
  XLSX.writeFile(workbook, fullFilename)

  console.log(`成功导出 ${data.length} 条数据到 ${fullFilename}`)
}

/**
 * 将多个数据表导出到同一个 Excel 文件的不同工作表
 * @param sheetsData 工作表数据数组，格式为 [{ name: string, data: any[], headers?: string[] }]
 * @param filename 文件名（不包含扩展名）
 */
export const exportMultipleSheetsToExcel = (
  sheetsData: { name: string; data: any[]; headers?: string[] }[],
  filename: string
) => {
  if (!sheetsData || sheetsData.length === 0) {
    console.warn('没有数据可以导出')
    return
  }

  // 创建工作簿
  const workbook = XLSX.utils.book_new()

  sheetsData.forEach(sheet => {
    if (!sheet.data || sheet.data.length === 0) {
      console.warn(`工作表 ${sheet.name} 没有数据，跳过`)
      return
    }

    // 获取列名
    let sheetHeaders: string[]
    if (sheet.headers && sheet.headers.length > 0) {
      sheetHeaders = sheet.headers
    } else {
      sheetHeaders = Object.keys(sheet.data[0])
    }

    // 准备工作表数据
    const worksheetData = []

    // 添加表头
    worksheetData.push(sheetHeaders)

    // 添加数据行
    sheet.data.forEach(row => {
      const values = sheetHeaders.map(header => {
        const value = row[header]
        return value === null || value === undefined ? '' : value
      })
      worksheetData.push(values)
    })

    // 创建工作表
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)

    // 设置列宽
    const columnWidths = sheetHeaders.map((header, index) => {
      let maxLength = header.length
      sheet.data.forEach(row => {
        const value = row[header] || ''
        const length = String(value).length
        if (length > maxLength) {
          maxLength = length
        }
      })
      const width = Math.max(10, Math.min(50, maxLength + 2))
      return { width: width }
    })
    worksheet['!cols'] = columnWidths

    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(workbook, worksheet, sheet.name)
  })

  // 生成文件名（包含时间戳）
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  const fullFilename = `${filename}_${timestamp}.xlsx`

  // 导出文件
  XLSX.writeFile(workbook, fullFilename)

  console.log(`成功导出 ${sheetsData.length} 个工作表到 ${fullFilename}`)
}