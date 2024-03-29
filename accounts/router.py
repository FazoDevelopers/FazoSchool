from rest_framework.routers import SimpleRouter
from . import views

router=SimpleRouter()
router.register("users",views.UserView,basename="user")
router.register("types-admin",views.Type_of_Admin_View,basename="types")
router.register("permissions-admin",views.Permission_View,basename="permissions")
router.register("admins",views.Admin_View,basename="admins")
router.register("teachers",views.Teacher_View,basename="teachers")
router.register("employers",views.Employer_View,basename="employers")
router.register("students",views.Student_View,basename="students")
router.register("student_discounts",views.StudentDiscount_View,basename="student_discounts")
router.register("student_log",views.StudentLog_View,basename="student_log")
router.register("parents",views.Parent_View,basename="parents")