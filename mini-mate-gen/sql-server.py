import json
import httpx
from typing import Any
import pymysql
import csv
import os
from datetime import datetime
from decimal import Decimal
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("SQLServer")
USER_AGENT = "SQLserver-app/1.0"

def _to_jsonable(value):
    if isinstance(value, Decimal):
        try:
            return float(value)
        except Exception:
            return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)

@mcp.tool()
async def sql_inter(sql_query):
    """
    查询本地MySQL数据库，通过运行一段SQL代码来进行数据库查询。\
    :param sql_query: 字符串形式的SQL查询语句，用于执行对MySQL中plan_dms_ds_20251222数据库中各张表进行查询，并获得各表中的各类相关信息
    :return：sql_query在MySQL中的运行结果。
    """
    
    connection = pymysql.connect(
            host='localhost',  # 数据库地址
            user='root',  # 数据库用户名
            passwd='root',  # 数据库密码
            db='plan_dms_ds_20251222',  # 数据库名
            charset='utf8'  # 字符集选择utf8
        )
    
    try:
        with connection.cursor() as cursor:
            # SQL查询语句
            sql = sql_query
            cursor.execute(sql)

            # 获取查询结果
            results = cursor.fetchall()
            json_rows = []
            for row in results:
                json_rows.append([_to_jsonable(v) for v in row])
            return json.dumps(json_rows, ensure_ascii=False)

    finally:
        connection.close()
    
@mcp.tool()
async def export_table_to_csv(table_name, output_file):
    """
    将 MySQL 数据库中的某个表导出为 CSV 文件。
    
    :param table_name: 需要导出的表名
    :param output_file: 输出的 CSV 文件路径
    """
    # 连接 MySQL 数据库
    connection = pymysql.connect(
        host='localhost',  # 数据库地址
        user='root',  # 数据库用户名
        passwd='root',  # 数据库密码
        db='plan_dms_ds_20251222',  # 数据库名
        charset='utf8'  # 字符集
    )

    try:
        with connection.cursor() as cursor:
            # 查询数据表的所有数据
            query = f"SELECT * FROM {table_name};"
            cursor.execute(query)

            # 获取所有列名
            column_names = [desc[0] for desc in cursor.description]

            # 获取查询结果
            rows = cursor.fetchall()

            # 确保输出目录存在
            dirpath = os.path.dirname(output_file)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)

            # 将数据写入 CSV 文件
            with open(output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # 写入表头
                writer.writerow(column_names)
                
                # 写入数据
                for row in rows:
                    writer.writerow([str(_to_jsonable(v)) for v in row])

            return json.dumps({"ok": True, "table": table_name, "rows": len(rows), "file": output_file}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

    finally:
        connection.close()

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')
