"""Default ODCS contract template and field type definitions."""

DEFAULT_CONTRACT = """\
dataContractSpecification: 1.1.0
id: urn:datacontract:com:example:orders
info:
  title: Orders Data Contract
  version: 1.0.0
  description: |
    Contract for the orders domain.
    Owned by the data engineering team.
  owner: data-engineering
  status: draft
  tags:
    - orders
    - ecommerce

servers:
  production:
    type: databricks
    catalog: main
    schema: sales

terms:
  usage: Internal analytics only
  limitations: No PII redistribution
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
        minimum: 0
      status:
        type: string
        required: true
        description: Order lifecycle status
        enum:
          - pending
          - processing
          - shipped
          - delivered
          - cancelled

servicelevels:
  availability:
    description: Guaranteed uptime
    percentage: "99.9%"
  freshness:
    description: Data latency SLA
    threshold: 1h
  support:
    time: 9x5
    responseTime: 1h

quality:
  type: SodaCL
  specification:
    checks for orders:
      - row_count > 0
      - missing_count(order_id) = 0
      - duplicate_count(order_id) = 0
"""

FIELD_TYPES = [
    "string", "integer", "long", "float", "double",
    "boolean", "date", "timestamp", "bytes", "array",
    "object", "record", "null",
]

STATUS_OPTIONS = ["draft", "active", "deprecated", "retired"]

SERVER_TYPES = ["databricks", "bigquery", "snowflake", "postgres",
                "mysql", "s3", "azure", "gcs", "kafka", "local"]
