class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = self._normalize(errors)
        super().__init__("Ошибка валидации")

    def _normalize(self, errors):
        normalized = {}

        if isinstance(errors, list):  # Pydantic
            for err in errors:
                field = err.get("loc", ["field"])[0]
                msg = err.get("msg", "Ошибка")

                # Чистим "Value error, ..."
                if msg.startswith("Value error, "):
                    msg = msg.replace("Value error, ", "")

                normalized[field] = msg

        elif isinstance(errors, dict):
            normalized = errors

        else:
            normalized["non_field"] = str(errors)

        return normalized
