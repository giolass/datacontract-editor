"""Templates y constantes para Source Data Contract (ODCS v3.1.0 + DQX)."""
import yaml

# ── Opciones de campos ────────────────────────────────────────────────────────
STATUS_OPTIONS    = ["draft", "active", "deprecated", "retired"]
SERVER_TYPES      = ["oracle", "sqlserver", "postgres", "mysql", "databricks",
                     "bigquery", "snowflake", "s3", "azure", "gcs", "kafka", "sftp", "local"]
ENVIRONMENTS      = ["production", "staging", "development", "qa", "sandbox"]
LOGICAL_TYPES     = ["string", "integer", "long", "float", "double", "number",
                     "boolean", "date", "timestamp", "bytes", "array", "object", "record"]
PHYSICAL_TYPES_MAP = {
    "oracle":     ["VARCHAR2(n)", "NUMBER(p,s)", "INTEGER", "DATE", "TIMESTAMP(6)", "CHAR(n)", "CLOB", "BLOB", "NUMBER(10)", "NUMBER(15,2)"],
    "sqlserver":  ["VARCHAR(n)", "INT", "BIGINT", "DECIMAL(p,s)", "DATE", "DATETIME2", "NVARCHAR(n)", "BIT"],
    "postgres":   ["VARCHAR(n)", "INTEGER", "BIGINT", "NUMERIC(p,s)", "DATE", "TIMESTAMP", "TEXT", "BOOLEAN", "UUID"],
    "mysql":      ["VARCHAR(n)", "INT", "BIGINT", "DECIMAL(p,s)", "DATE", "DATETIME", "TEXT", "TINYINT"],
    "databricks": ["STRING", "INT", "BIGINT", "DOUBLE", "DECIMAL(p,s)", "DATE", "TIMESTAMP", "BOOLEAN", "ARRAY<>", "STRUCT<>"],
    "default":    ["string", "integer", "number", "boolean", "date", "timestamp", "text"],
}
CLASSIFICATION    = ["public", "internal", "confidential", "restricted", "pii"]
SLA_DRIVERS       = ["operational", "analytics", "regulatory"]
SLA_UNITS         = ["percent", "h", "min", "d", "month", "year", "MB", "GB"]
TEAM_ROLES        = ["owner", "data steward", "consumer", "producer",
                     "data engineer", "data scientist", "data protection officer", "admin"]
ACCESS_TYPES      = ["read", "write", "read-write", "admin"]
DQ_DIMENSIONS     = ["completeness", "validity", "accuracy", "uniqueness",
                     "consistency", "timeliness", "integrity"]
DQ_SEVERITY       = ["error", "warning", "info"]
DQ_DRIVERS        = ["operational", "analytics", "regulatory"]

# DQX row-level check functions
DQX_ROW_CHECKS = [
    "is_not_null", "is_null", "is_not_empty", "is_not_null_and_not_empty",
    "is_in_list", "is_not_null_and_is_in_list", "is_not_in_list",
    "is_in_range", "is_not_in_range",
    "is_not_less_than", "is_not_greater_than",
    "is_equal_to", "is_not_equal_to",
    "is_valid_date", "is_valid_timestamp", "is_not_in_future",
    "is_data_fresh", "regex_match",
    "is_unique",                        # dataset-level
    "is_aggr_not_less_than",            # dataset-level
    "is_aggr_not_greater_than",         # dataset-level
    "foreign_key",                      # dataset-level
    "sql_expression",                   # custom SQL
]

DQX_CRITICALITY = ["error", "warn"]

# ── SERVER extra fields per type ──────────────────────────────────────────────
SERVER_FIELDS = {
    "oracle":     ["host", "port", "database", "schema"],
    "sqlserver":  ["host", "port", "database", "schema"],
    "postgres":   ["host", "port", "database", "schema"],
    "mysql":      ["host", "port", "database", "schema"],
    "databricks": ["catalog", "schema"],
    "bigquery":   ["project", "dataset"],
    "snowflake":  ["account", "database", "schema", "warehouse"],
    "s3":         ["location"],
    "azure":      ["location"],
    "gcs":        ["location"],
    "kafka":      ["host", "port"],
    "sftp":       ["host", "port", "path"],
    "local":      ["path"],
}

# ── Default Source Data Contract ──────────────────────────────────────────────
DEFAULT_CONTRACT = yaml.dump({
    "kind": "DataContract",
    "apiVersion": "v3.1.0",
    "id": "urn:datacontract:bpt:domain:source-name",
    "name": "Source Data Contract",
    "version": "1.0.0",
    "status": "draft",
    "domain": "",
    "dataProduct": "",
    "tenant": "BPT",
    "description": {
        "purpose": "",
        "limitations": "",
        "usage": ""
    },
    "tags": [],
    "servers": [
        {
            "server": "production",
            "type": "oracle",
            "environment": "production",
            "host": "",
            "port": 1521,
            "database": "",
            "schema": "",
            "description": ""
        }
    ],
    "schema": [
        {
            "name": "table_name",
            "physicalName": "SCHEMA.TABLE_NAME",
            "physicalType": "TABLE",
            "description": "",
            "tags": [],
            "properties": [
                {
                    "name": "id",
                    "businessName": "Identifier",
                    "logicalType": "string",
                    "physicalType": "VARCHAR2(20)",
                    "primaryKey": True,
                    "required": True,
                    "unique": True,
                    "description": "Primary key",
                    "classification": "internal",
                    "tags": ["pk"]
                }
            ]
        }
    ],
    "quality": [
        {
            "rule": "id_not_null",
            "description": "Primary key must not be null",
            "dimension": "completeness",
            "type": "library",
            "severity": "error",
            "businessImpact": "operational",
            "element": "table_name.id"
        }
    ],
    "dqx_checks": {
        "table_name": [
            {
                "criticality": "error",
                "name": "id_is_not_null",
                "check": {
                    "function": "is_not_null",
                    "arguments": {"column": "id"}
                }
            }
        ]
    },
    "team": [
        {
            "username": "",
            "name": "",
            "email": "",
            "role": "owner",
            "dateIn": "2024-01-01"
        }
    ],
    "slaProperties": [
        {"property": "availability", "value": 99.5, "unit": "percent", "driver": "operational", "description": ""},
        {"property": "freshness",    "value": 1,    "unit": "h",       "driver": "analytics",  "description": ""},
        {"property": "retention",    "value": 1,    "unit": "year",    "driver": "regulatory", "description": ""},
        {"property": "frequency",    "value": "daily", "driver": "operational", "scheduler": "cron", "schedule": "0 1 * * *"}
    ],
    "customProperties": [
        {"property": "databricksCatalog",     "value": ""},
        {"property": "databricksSchema",      "value": ""},
        {"property": "databricksTargetTable", "value": ""},
        {"property": "ingestionTool",         "value": "Apache Spark / Databricks Jobs"},
        {"property": "sourceSystem",          "value": ""},
        {"property": "encryptionRequired",    "value": True}
    ]
}, allow_unicode=True, sort_keys=False, default_flow_style=False)
