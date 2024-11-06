"""
URL configuration for yono project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from myapp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/',include('yono.api.urls')),
    path('api/insertAttendance/', insertAttendance,name="insertAttendance"),
    path('api/getCoursesForFaculty/',getCoursesForFaculty,name="getCoursesForFaculty"),
    path('api/getStudentsFromCourseCode/',getStudentsFromCourseCode,name="getStudentsFromCourseCode"),
    path('api/getCoursesForStudents/',getCoursesForStudents,name="getCoursesForStudents"),
    path('api/loginUser/',loginUser,name="loginUser"),
    path('api/getUserDetails/',getUserDetails,name="getUserDetails"),
    path('api/getAttendanceDetailsForStudent/',getAttendanceDetailsForStudent,name="getAttendanceDetailsForStudent"),
    path('api/addResult/',addResult,name="Add Result"),
    path('api/getStudentsFromCourseCodeForResult/',getStudentsFromCourseCodeForResult,name='getStudentsFromCourseCodeForResult'),
    path('api/getResultForStudentForCourse/',getResultForStudentForCourse,name="getResultForStudentForCourse"),
    path('api/getTodosForUser/',getTodosForUser,name='getTodosForUser'),
    path('api/addTimetable/', addTimetable, name='addTimetable'),
    path('api/reschedule_class/', reschedule_class, name='reschedule_class'),
    path('api/add_or_change_class/', add_or_change_class,name='add_or_change_class'),
    path('api/cancel_class/', cancel_class, name='cancel_class'),
    path('api/getTimetableForStudent/',getTimetableForStudent,name="getTimetableForStudent"),
    path('api/getCalendarId/',getCalendarId,name="getCalendarId"),

    # mahitha
    path('api/search/',search,name="search"),
    path('api/getFeeDefaulters/',getFeeDefaulters,name="getFeeDefaulters"),
    path('api/sendMessage/',sendMessage,name="sendMessage"),
    path('api/getMessages/',getMessages,name="getMessages"),
    path('api/acceptMessage/',acceptMessage,name="acceptMessage"),
    path('api/getCertificates/',getCertificates,name="getCertificates"),
    path('api/acceptCertificate/',acceptCertificate,name="acceptCertificate"),
    path('api/checkMessageStatus/',checkMessageStatus,name="checkMessageStatus"),
    path('api/sendCertificate/',sendCertificate,name="sendCertificate"),
    path('api/checkCertificateStatus/',checkCertificateStatus,name="checkCertificateStatus"),
    path('api/getEachClassStudentsList/',getEachClassStudentsList,name="getEachClassStudentsList"),
    path('api/addNewStudent/',addNewStudent,name="addNewStudent"),
    path('api/updateSemester/',updateSemester,name="updateSemester"),
    path('api/getUserAllDetails/', getUserAllDetails, name='getUserAllDetails'),

    path('api/facultyTimetable/', facultyTimetable, name='facultyTimetable'),
    path('api/getFacultySchedule/', getFacultySchedule, name='getFacultySchedule'),

    path('api/getTimeSlotForFaculty/',getTimeSlotForFaculty,name='getTimeSlotForFaculty'),
    path('api/getStudentsWithAttendanceShortage/',getStudentsWithAttendanceShortage,name='getStudentsWithAttendanceShortage'),
path('api/getLabResultForStudentForCourse/', getLabResultForStudentForCourse, name='getLabResultForStudentForCourse'),
    path('api/getCourseType/', getCourseType, name='getCourseType'),
    path('api/addResultLab/', addResultLab, name='addResultLab'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)