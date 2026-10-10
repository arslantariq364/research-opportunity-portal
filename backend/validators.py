"""
Validation utilities for University Research Opportunity Portal.
Phase 2: Comprehensive request validation for REST API endpoints.
"""
import re
from datetime import datetime

# Permitted fields for research opportunities
ALLOWED_FIELDS = {
    'title',
    'description',
    'research_area',
    'faculty_name',
    'department',
    'required_skills',
    'available_positions',
    'application_deadline',
    'status'
}

# Fields required during opportunity creation (POST)
REQUIRED_POST_FIELDS = {
    'title',
    'description',
    'research_area',
    'faculty_name',
    'department',
    'required_skills',
    'available_positions',
    'application_deadline'
}

# String fields that require non-empty, non-whitespace content
STRING_FIELDS = {
    'title',
    'description',
    'research_area',
    'faculty_name',
    'department',
    'required_skills'
}

VALID_STATUSES = {'Open', 'Closed'}


def _validate_string_field(field_name, value):
    """Validate that value is a non-empty, trimmed string."""
    if not isinstance(value, str):
        return f"'{field_name}' must be a string."
    if not value.strip():
        return f"'{field_name}' cannot be empty or whitespace-only."
    return None


def _validate_available_positions(value):
    """Validate that available_positions is a positive integer > 0."""
    # In Python, bool is a subclass of int, so isinstance(True, int) is True!
    if isinstance(value, bool) or not isinstance(value, int):
        return "'available_positions' must be an integer."
    if value <= 0:
        return "'available_positions' must be a positive integer greater than zero."
    return None


def _validate_application_deadline(value):
    """Validate that application_deadline is formatted as YYYY-MM-DD and is a real date."""
    if not isinstance(value, str):
        return "'application_deadline' must be a date string formatted as YYYY-MM-DD."
    
    # Strictly check YYYY-MM-DD format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return "'application_deadline' must be formatted as YYYY-MM-DD."
    
    try:
        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
        return None, parsed_date
    except ValueError:
        return "'application_deadline' is an impossible or invalid calendar date.", None


def _validate_status(value):
    """Validate that status is either 'Open' or 'Closed'."""
    if not isinstance(value, str):
        return "'status' must be a string."
    if value not in VALID_STATUSES:
        return f"'status' must be either 'Open' or 'Closed' (got '{value}')."
    return None


def validate_create_opportunity(data):
    """
    Validate JSON payload for creating a new research opportunity (POST).
    Returns (is_valid: bool, cleaned_data: dict, errors: dict).
    """
    if not isinstance(data, dict):
        return False, {}, {"payload": "Request body must be a valid JSON object."}

    errors = {}

    # 1. Check for unsupported/unexpected fields
    submitted_keys = set(data.keys())
    unexpected_keys = submitted_keys - ALLOWED_FIELDS
    if unexpected_keys:
        for key in sorted(unexpected_keys):
            errors[key] = f"Unsupported field '{key}' is not allowed."
        return False, {}, errors

    # 2. Check for missing required fields
    missing_keys = REQUIRED_POST_FIELDS - submitted_keys
    if missing_keys:
        for key in sorted(missing_keys):
            errors[key] = f"Field '{key}' is required."
        return False, {}, errors

    cleaned_data = {}

    # 3. Validate string fields
    for field in STRING_FIELDS:
        err = _validate_string_field(field, data[field])
        if err:
            errors[field] = err
        else:
            cleaned_data[field] = data[field].strip()

    # 4. Validate available_positions
    pos_err = _validate_available_positions(data['available_positions'])
    if pos_err:
        errors['available_positions'] = pos_err
    else:
        cleaned_data['available_positions'] = data['available_positions']

    # 5. Validate application_deadline
    deadline_res = _validate_application_deadline(data['application_deadline'])
    if isinstance(deadline_res, tuple):
        date_err, parsed_date = deadline_res
        if date_err:
            errors['application_deadline'] = date_err
        else:
            cleaned_data['application_deadline'] = parsed_date
    else:
        errors['application_deadline'] = deadline_res

    # 6. Validate status (defaults to 'Open' if omitted)
    if 'status' in data:
        status_err = _validate_status(data['status'])
        if status_err:
            errors['status'] = status_err
        else:
            cleaned_data['status'] = data['status']
    else:
        cleaned_data['status'] = 'Open'

    is_valid = len(errors) == 0
    return is_valid, cleaned_data if is_valid else {}, errors


def validate_update_opportunity(data):
    """
    Validate JSON payload for updating an existing research opportunity (PUT).
    Supports partial updates while strictly validating supplied fields.
    Returns (is_valid: bool, cleaned_data: dict, errors: dict).
    """
    if not isinstance(data, dict):
        return False, {}, {"payload": "Request body must be a valid JSON object."}

    if not data:
        return False, {}, {"payload": "Request body must contain at least one field to update."}

    errors = {}

    # 1. Check for unsupported/unexpected fields
    submitted_keys = set(data.keys())
    unexpected_keys = submitted_keys - ALLOWED_FIELDS
    if unexpected_keys:
        for key in sorted(unexpected_keys):
            errors[key] = f"Unsupported field '{key}' is not allowed."
        return False, {}, errors

    cleaned_data = {}

    # 2. Validate only supplied fields
    for field in submitted_keys:
        val = data[field]
        if field in STRING_FIELDS:
            err = _validate_string_field(field, val)
            if err:
                errors[field] = err
            else:
                cleaned_data[field] = val.strip()
        elif field == 'available_positions':
            err = _validate_available_positions(val)
            if err:
                errors[field] = err
            else:
                cleaned_data[field] = val
        elif field == 'application_deadline':
            deadline_res = _validate_application_deadline(val)
            if isinstance(deadline_res, tuple):
                date_err, parsed_date = deadline_res
                if date_err:
                    errors[field] = date_err
                else:
                    cleaned_data[field] = parsed_date
            else:
                errors[field] = deadline_res
        elif field == 'status':
            err = _validate_status(val)
            if err:
                errors[field] = err
            else:
                cleaned_data[field] = val

    is_valid = len(errors) == 0
    return is_valid, cleaned_data if is_valid else {}, errors
