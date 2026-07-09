import os, sys
for k in list(sys.modules.keys()):
    if any(x in k for x in ['database','routes','app','config']):
        del sys.modules[k]
from app import create_app, db
app = create_app()

with app.test_client() as client:
    # Login
    resp = client.post('/auth/login', data={'username':'admin','password':'admin123'}, follow_redirects=True)
    print('Login:', resp.status_code)

    # Add student
    resp = client.post('/admin/students/add', data={
        'username':'alice','email':'a@t.com','password':'pass123',
        'full_name':'Alice Wong','student_id':'S001','department':'CS','semester':3,
    }, follow_redirects=True)
    print('Add status:', resp.status_code)
    print('Add redirect path:', resp.request.path)
    print('Add has Alice:', b'Alice' in resp.data)
    
    # Check students page for Alice
    resp = client.get('/admin/students', follow_redirects=True)
    print('Students page has S001:', b'S001' in resp.data)
    print('Students page has Alice:', b'Alice' in resp.data)

    # Check student ID by looking at the data
    from database.models import Student, User
    s = Student.query.first()
    print('Student in DB:', s.id, s.student_id, s.user.full_name)

    # Edit
    resp = client.get(f'/admin/students/edit/{s.id}', follow_redirects=True)
    print(f'Edit /{s.id} status:', resp.status_code)
    print(f'Edit has Alice:', b'Alice' in resp.data)

    # Delete
    resp = client.post(f'/admin/students/delete/{s.id}', follow_redirects=True)
    print(f'Delete /{s.id} status:', resp.status_code)
    print('After delete, students page:', resp.request.path)
    print('Has No students:', b'No students' in resp.data)
