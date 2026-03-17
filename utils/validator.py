"""YAML validation against basic ODCS rules (no external deps required)."""
import yaml
import re
from dataclasses import dataclass, field
from typing import List


REQUIRED_INFO_KEYS = ["title", "version", "owner"]
VALID_FIELD_TYPES = {
    "string", "integer", "long", "float", "double",
    "boolean", "date", "timestamp", "bytes", "array",
    "object", "record", "null",
}
VALID_STATUSES = {"draft", "active", "deprecated", "retired"}


@dataclass
class ValidationIssue:
    severity: str   # "error" | "warning" | "info"
    path: str
    message: str


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self):
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def infos(self):
        return [i for i in self.issues if i.severity == "info"]

    @property
    def is_valid(self):
        return len(self.errors) == 0


def validate_yaml(yaml_str: str) -> ValidationResult:
    result = ValidationResult()

    # 1. Parse YAML
    try:
        doc = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        result.issues.append(ValidationIssue("error", "root", f"YAML parse error: {e}"))
        return result

    if not isinstance(doc, dict):
        result.issues.append(ValidationIssue("error", "root", "Contract must be a YAML mapping"))
        return result

    # 2. Spec version
    spec = doc.get("dataContractSpecification")
    if not spec:
        result.issues.append(ValidationIssue("error", "dataContractSpecification",
                                             "Missing required field: dataContractSpecification"))
    else:
        result.issues.append(ValidationIssue("info", "dataContractSpecification",
                                             f"Spec version: {spec}"))

    # 3. Contract ID
    cid = doc.get("id", "")
    if not cid:
        result.issues.append(ValidationIssue("error", "id", "Missing required field: id"))
    elif not cid.startswith("urn:"):
        result.issues.append(ValidationIssue("warning", "id",
                                             "Contract id should follow URN format: urn:datacontract:..."))

    # 4. Info block
    info = doc.get("info", {})
    if not info:
        result.issues.append(ValidationIssue("error", "info", "Missing required block: info"))
    else:
        for k in REQUIRED_INFO_KEYS:
            if not info.get(k):
                result.issues.append(ValidationIssue("error", f"info.{k}",
                                                     f"info.{k} is required"))
        status = info.get("status", "")
        if status and status not in VALID_STATUSES:
            result.issues.append(ValidationIssue("warning", "info.status",
                                                 f"Unknown status '{status}'. Valid: {VALID_STATUSES}"))
        version = info.get("version", "")
        if version and not re.match(r"^\d+\.\d+\.\d+", str(version)):
            result.issues.append(ValidationIssue("warning", "info.version",
                                                 "Version should follow semver (e.g. 1.0.0)"))

    # 5. Models
    models = doc.get("models", {})
    if not models:
        result.issues.append(ValidationIssue("warning", "models",
                                             "No models defined — contract has no schema"))
    else:
        for tname, tdef in models.items():
            if not isinstance(tdef, dict):
                result.issues.append(ValidationIssue("error", f"models.{tname}",
                                                     "Model definition must be a mapping"))
                continue
            fields = tdef.get("fields", {})
            if not fields:
                result.issues.append(ValidationIssue("warning", f"models.{tname}",
                                                     f"Table '{tname}' has no fields defined"))
            else:
                for fname, fdef in fields.items():
                    if not isinstance(fdef, dict):
                        continue
                    ftype = fdef.get("type", "")
                    if ftype and ftype not in VALID_FIELD_TYPES:
                        result.issues.append(ValidationIssue("warning",
                                                             f"models.{tname}.{fname}.type",
                                                             f"Unknown type '{ftype}'"))

    # 6. Good practice checks
    if doc.get("models") and not doc.get("servicelevels"):
        result.issues.append(ValidationIssue("info", "servicelevels",
                                             "Consider adding servicelevels (SLAs)"))
    if not doc.get("terms"):
        result.issues.append(ValidationIssue("info", "terms",
                                             "Consider adding usage terms"))

    return result
