from wtforms.fields import DateField


class GovDateField(DateField):
    """DateField that can parse month strings like 'January' or 'Jan' into numeric format."""

    MONTH_MAP = {
        # Full month names
        "january": "1",
        "february": "2",
        "march": "3",
        "april": "4",
        "may": "5",
        "june": "6",
        "july": "7",
        "august": "8",
        "september": "9",
        "october": "10",
        "november": "11",
        "december": "12",
        # Short month names
        "jan": "1",
        "feb": "2",
        "mar": "3",
        "apr": "4",
        "jun": "6",
        "jul": "7",
        "aug": "8",
        "sep": "9",
        "oct": "10",
        "nov": "11",
        "dec": "12",
        # Alternative short forms
        "sept": "9",
    }

    def _process_date_list(self, date_list):
        """Convert month strings to numbers in a date list [day, month, year]."""
        if not isinstance(date_list, list) or len(date_list) != 3:
            return date_list

        day, month, year = date_list

        # Try to convert month string to number
        if isinstance(month, str) and month.lower() in self.MONTH_MAP:
            month = self.MONTH_MAP[month.lower()]

        return [day, month, year]

    def process_formdata(self, valuelist):
        if valuelist:
            # Store the original raw data for validation later
            self._original_raw_data = valuelist

            # Convert month strings to numbers before processing
            processed_valuelist = self._process_date_list(valuelist)

            try:
                if len(processed_valuelist) == 3:
                    day, month, year = processed_valuelist
                    if day and month and year:
                        from datetime import datetime

                        self.data = datetime.strptime(f"{day} {month} {year}", "%d %m %Y").date()
                    else:
                        self.data = None
                else:
                    self.data = None
            except (ValueError, TypeError):
                self.data = None
        else:
            self._original_raw_data = valuelist
            self.data = None
