import os

# Admin Dashboard Content (Fixed Syntax + Correct Column Order)
admin_dashboard_content = """{% extends 'base.html' %}

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
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No students found matching the criteria.</p>
        {% endif %}
    </div>
</div>
{% endblock %}"""

# Exam Dashboard Content (Fixed Syntax + Correct Column Order)
exam_dashboard_content = """{% extends 'base.html' %}

{% block title %}Exam Branch Dashboard - EduPay{% endblock %}

{% block content %}
<div class="card wide">
    <div class="welcome-box">
        <h3>Exam Branch Dashboard</h3>
        <p>Manage semester exams and view reports.</p>
        <a href="{% url 'add_exam' %}" class="btn" style="background:#27ae60;">+ Add New Exam</a>
    </div>

    <!-- Exam Management Section -->
    <div class="exam-management-section"
        style="margin-top: 30px; padding: 20px; background: #fff; border-radius: 8px; border: 1px solid #ddd;">
        <h4>Manage Exams</h4>
        <form method="post" action="."
            style="display: grid; gap: 15px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
            {% csrf_token %}
            {% for field in exam_form %}
            <div class="form-group">
                <label for="{{ field.id_for_label }}" style="display: block; margin-bottom: 5px; font-weight: 500;">{{
                    field.label }}</label>
                {{ field }}
                {% if field.errors %}
                <span style="color: red; font-size: 12px;">{{ field.errors.0 }}</span>
                {% endif %}
            </div>
            {% endfor %}
            <div style="grid-column: 1 / -1;">
                <button type="submit" name="add_exam" class="btn" style="background: #27ae60; cursor: pointer;">Save
                    Exam Fee Details</button>
            </div>
        </form>
    </div>

    <!-- Student List Section (Replicated from Admin) -->
    <div style="margin-top: 30px;">
        <h3>Registered Students</h3>

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
                <a href="{% url 'exam_dashboard' %}" class="btn"
                    style="background: #e74c3c; line-height:38px; display:inline-block; height:38px; text-decoration:none; width: auto; min-width: 120px; padding: 0 20px; flex: 0 0 auto; text-align: center;">Reset</a>
                <button type="button" onclick="window.print()" class="btn"
                    style="background: #34495e; height: 38px; cursor: pointer; width: auto; min-width: 120px; padding: 0 20px; flex: 0 0 auto;">Print
                    List</button>
            </form>
        </div>

        {% if students %}
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f2f2f2;">
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Roll Number</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Name</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Branch</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Year</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Email</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;">{{ student.roll_number }}</td>
                        <td style="padding: 10px;">{{ student.full_name }}</td>
                        <td style="padding: 10px;">{{ student.branch }}</td>
                        <td style="padding: 10px;">{{ student.get_year_display }}</td>
                        <td style="padding: 10px;">{{ student.user.email }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p>No students found matching the criteria.</p>
        {% endif %}
    </div>


</div>

<div class="transactions-section">
    <h3>Recent Successful Transactions</h3>
    {% if transactions %}
    <table>
        <thead>
            <tr>
                <th>Transaction ID</th>
                <th>Student</th>
                <th>Exam</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for txn in transactions %}
            <tr>
                <td>{{ txn.payment_id }}</td>
                <td>{{ txn.student.student_profile.roll_number }} ({{ txn.student.mobile_number }})</td>
                <td>{{ txn.exam.name }}</td>
                <td>₹{{ txn.amount }}</td>
                <td>{{ txn.timestamp }}</td>
                <td>{{ txn.status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>No transactions found.</p>
    {% endif %}
</div>
</div>
{% endblock %}"""

base_dir = r"d:/0803/users/templates/users"
admin_path = os.path.join(base_dir, "admin_dashboard.html")
exam_path = os.path.join(base_dir, "exam_dashboard.html")

with open(admin_path, "w", encoding='utf-8') as f:
    f.write(admin_dashboard_content)
    print(f"Overwrote {admin_path}")

with open(exam_path, "w", encoding='utf-8') as f:
    f.write(exam_dashboard_content)
    print(f"Overwrote {exam_path}")
