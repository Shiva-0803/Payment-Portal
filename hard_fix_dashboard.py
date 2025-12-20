import os

file_path = r"d:\0803\users\templates\users\admin_dashboard.html"

content = """{% extends 'base.html' %}

{% block title %}Admin Dashboard - EduPay{% endblock %}

{% block content %}
<div class="card wide">
    <div class="welcome-box">
        <h3>Admin Dashboard</h3>
        <p>Manage students and view registrations.</p>
    </div>

    <!-- Filter Form -->
    <div class="filter-section" style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
        <form method="get" action="." style="display: flex; gap: 15px; align-items: flex-end;">
            <div class="form-group" style="margin-bottom: 0;">
                <label for="branch" style="display: block; margin-bottom: 5px;">Branch</label>
                <select name="branch" id="branch" style="padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                    <option value="">All Branches</option>
                    {% for code, name in branch_choices %}
                    <option value="{{ code }}" {% if selected_branch == code %}selected{% endif %}>{{ name }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group" style="margin-bottom: 0;">
                <label for="year" style="display: block; margin-bottom: 5px;">Year</label>
                <select name="year" id="year" style="padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                    <option value="">All Years</option>
                    {% for year_val, label in year_choices %}
                    <option value="{{ year_val }}" {% if selected_year == year_val %}selected{% endif %}>{{ label }}
                    </option>
                    {% endfor %}
                </select>
            </div>

            <button type="submit" class="btn"
                style="height: 38px; width: auto; min-width: 120px; padding: 0 20px; flex: 0 0 auto;">Filter</button>
            <a href="{% url 'admin_dashboard' %}" class="btn"
                style="background: #e74c3c; line-height:38px; display:inline-block; height:38px; text-decoration:none; width: auto; min-width: 120px; padding: 0 20px; flex: 0 0 auto; text-align: center;">Reset</a>
            <a href="{% url 'paid_students_list' %}" class="btn"
                style="background: #27ae60; line-height:38px; display:inline-block; height:38px; text-decoration:none; width: auto; min-width: 120px; padding: 0 20px; flex: 0 0 auto; text-align: center;">Paid
                Students</a>
            <button type="button" onclick="window.print()" class="btn"
                style="background: #34495e; height: 38px; cursor: pointer; border: none; color: white; padding: 0 20px; border-radius: 4px; width: auto; min-width: 120px; flex: 0 0 auto;">Print
                List</button>
        </form>
    </div>

    <!-- Students Table -->
    <div class="students-section">
        <h3>Registered Students ({{ students.count }})</h3>
        {% if students %}
        <table>
            <thead>
                <tr>
                    <th>Roll Number</th>
                    <th>Name</th>
                    <th>Branch</th>
                    <th>Year</th>
                    <th>Email</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for student in students %}
                <tr>
                    <td>{{ student.roll_number }}</td>
                    <td>{{ student.full_name }}</td>
                    <td>{{ student.branch }}</td>
                    <td>{{ student.get_year_display }}</td>
                    <td>{{ student.user.email }}</td>
                    <td>
                        <a href="{% url 'edit_student' student.pk %}" class="btn"
                            style="background-color: #3498db; padding: 5px 10px; font-size: 0.9rem; margin-right: 5px;">Edit</a>
                        <a href="{% url 'delete_student' student.pk %}" class="btn"
                            style="background-color: #e74c3c; padding: 5px 10px; font-size: 0.9rem;"
                            onclick="return confirm('Are you sure you want to delete this student? This action cannot be undone.')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No students found matching the criteria.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully wrote to {file_path}")
