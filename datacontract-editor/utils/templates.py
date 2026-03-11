"""Default ODCS contract template and field type definitions."""

DEFAULT_CONTRACT = """\
dataContractSpecification: 1.1.0
id: urn:datacontract:bpt:example:orders
info:
  title: Orders Data Contract
  version: 1.0.0
  status: draft
  description: |
    Contract for the orders domain.
  owner: data-engineering
  ownerEmail: data-engineering@bpt.com.co
  dataProduct: orders-platform
  domain: sales
  contact:
    - name: Data Engineering Team
      email: data-engineering@bpt.com.co
      role: owner
  tags:
    - orders
    - ecommerce

servers:
  production:
    type: databricks
    catalog: main
    schema: sales
    environment: production
    description: Production Databricks workspace
    roles:
      - role: read
        groups: [analysts, data-scientists]

terms:
  usage: Internal analytics and reporting only
  limitations: No PII redistribution outside approved systems
  billing: Free
  noticePeriod: P3M

models:
  orders:
    description: All customer orders
    type: table
    fields:
      order_id:
        type: string
        required: true
        unique: true
        description: Unique order identifier
        example: "ORD-20240101-001"
      customer_id:
        type: string
        required: true
        description: Foreign key to customers table
      order_date:
        type: timestamp
        required: true
        description: When the order was placed
      total_amount:
        type: double
        required: true
        description: Total order value in USD

roles:
  - role: read
    access: read
    description: Read-only access for analysts and BI tools
  - role: write
    access: write
    description: Write access for ETL pipelines

support:
  channel: "#data-contracts"
  url: https://support.bpt.com.co
  on_call: data-oncall@bpt.com.co
  documentation: https://docs.bpt.com.co/data-contracts

pricing:
  billing: Free

servicelevels:
  availability:
    description: Percentage of time data is available
    percentage: "99.9%"
  freshness:
    description: Maximum data latency
    threshold: 1h
  retention:
    description: Data retention period
    period: 1 year
  latency:
    description: Query response time
    threshold: 5s
  support:
    time: 9x5
    responseTime: 1h
"""

FIELD_TYPES = [
    "string", "integer", "long", "float", "double",
    "boolean", "date", "timestamp", "bytes", "array",
    "object", "record", "null",
]

STATUS_OPTIONS = ["draft", "active", "deprecated", "retired"]

SERVER_TYPES = [
    "databricks", "bigquery", "snowflake", "postgres",
    "mysql", "sqlserver", "oracle", "s3", "azure",
    "gcs", "kafka", "local",
]

ENVIRONMENTS = ["production", "staging", "development", "qa", "sandbox"]

ACCESS_TYPES = ["read", "write", "read-write", "admin", "none"]

ROLE_OPTIONS = ["owner", "steward", "consumer", "producer", "analyst",
                "engineer", "scientist", "admin"]
