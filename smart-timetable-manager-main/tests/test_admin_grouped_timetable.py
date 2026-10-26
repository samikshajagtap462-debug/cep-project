import re


def test_admin_today_timetable_markup_elements():
    """Verify that admin.html contains the filter, active schedule badge, schedule button, and grouped container."""
    with open('smart-timetable-manager-main/admin.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Container for grouped cards
    assert 'id="admin-today-timetable-container"' in html, "admin-today-timetable-container must exist"

    # 2. Filter dropdown
    assert 'id="admin-today-class-filter"' in html, "admin-today-class-filter select element must exist"
    assert 'onchange="onAdminTodayClassFilterChange(this.value)"' in html, "Filter select must trigger onAdminTodayClassFilterChange"

    # 3. Active Schedule indicator
    assert 'Active Schedule' in html, "Active Schedule badge must exist"
    assert 'text-emerald-700 bg-emerald-50' in html, "Active Schedule styling must be preserved"

    # 4. Schedule Session button
    assert 'openScheduleSessionModal()' in html, "+ Schedule Session button with openScheduleSessionModal() must exist"


def test_admin_today_timetable_javascript_logic():
    """Verify JS implementation has grouping, filtering, chronological sorting, and 6 columns."""
    with open('smart-timetable-manager-main/admin.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Verify key JS functions exist
    assert "function groupLecturesByClassAndBatch(" in html, "groupLecturesByClassAndBatch function must exist"
    assert "function filterLecturesGroups(" in html, "filterLecturesGroups function must exist"
    assert "function updateAdminTodayClassFilterOptions(" in html, "updateAdminTodayClassFilterOptions function must exist"
    assert "function onAdminTodayClassFilterChange(" in html, "onAdminTodayClassFilterChange function must exist"
    assert "function renderAdminTodayTimetable(" in html, "renderAdminTodayTimetable function must exist"

    # Verify chronological sorting
    assert "localeCompare(bItem.startTime" in html or "localeCompare(b.startTime" in html, "Sessions must be sorted chronologically by startTime"

    # Verify the 6 required columns are present in table headers
    required_columns = ["Slot Time", "Course / Subject", "Faculty", "Room / Lab", "Status", "Actions"]
    for col in required_columns:
        assert f">{col}<" in html or f" {col} " in html, f"Column '{col}' must be present in table headers"

    # Verify edit session modal is linked to Action button
    assert "openEditSessionModal(" in html, "Actions column must call openEditSessionModal"
