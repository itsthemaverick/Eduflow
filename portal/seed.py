
from portal.models import Teacher, Lesson, LessonContent, TeacherLessonAssignment, LoginHistory, PartnerSchool, Review
from django.utils import timezone
import datetime

def seed_database():
    # Seed Partner Schools if none exist
    if not PartnerSchool.objects.exists():
        PartnerSchool.objects.create(
            name="Zilla Parishad Primary School, Khed",
            location="Pune District, Maharashtra",
            logo_url="https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&q=80&w=300",
            students_impacted="420+ Students",
            description="Pioneering STEM digital curriculum delivery across 8 rural primary classrooms."
        )
        PartnerSchool.objects.create(
            name="Community Learning Academy, Alwar",
            location="Alwar Region, Rajasthan",
            logo_url="https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=300",
            students_impacted="650+ Students",
            description="Focusing on foundational mathematics and bilingual literacy in tribal village clusters."
        )
        PartnerSchool.objects.create(
            name="Adarsh Vidya Mandir, Junnar",
            location="Western Ghats Division",
            logo_url="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&q=80&w=300",
            students_impacted="380+ Students",
            description="Equipped with solar-powered offline tablets for science experimentation lessons."
        )
        PartnerSchool.objects.create(
            name="Gramin Vikas Model School, Anand",
            location="Anand District, Gujarat",
            logo_url="https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&q=80&w=300",
            students_impacted="510+ Students",
            description="Integrating Project Jhep digital video masterclasses with daily teacher lesson planning."
        )

    # Seed Reviews if none exist
    if not Review.objects.exists():
        Review.objects.create(
            author_name="Anita Sharma",
            author_role="Grade 6 Mathematics Educator",
            school_name="Rajasthan Rural School District",
            author_avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=200",
            rating=5,
            content="Project Jhep transformed our geometry sessions! Even with unstable internet, downloading the offline lesson resources lets me run interactive paper-folding activities effortlessly."
        )
        Review.objects.create(
            author_name="Rajesh Kumar",
            author_role="Head of Science Faculty",
            school_name="Bihar Community Learning Hub",
            author_avatar="https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=200",
            rating=5,
            content="The video lectures and experiment walkthroughs give my students visual clarity they never had before. Student attendance and test scores have jumped significantly."
        )
        Review.objects.create(
            author_name="Sunita Patel",
            author_role="Primary English Instructor",
            school_name="Gujarat Tribal Belt Primary",
            author_avatar="https://images.unsplash.com/photo-1580894732413-80c8509c2794?auto=format&fit=crop&q=80&w=200",
            rating=5,
            content="Bilingual storytelling resources in Project Jhep helped bridge the language barrier for our rural students. The admin tracking dashboard makes reporting super simple."
        )

    # Only seed teachers if no teachers exist
    if Teacher.objects.exists():
        return


    print("Seeding database with initial NGO portal records...")

    # 1. Create Teachers
    t1 = Teacher.objects.create(
        username="anita.sharma",
        name="Anita Sharma",
        email="anita.sharma@ngoteach.org",
        school_region="Rajasthan Rural School District",
        subject_specialty="Mathematics & Logic",
        joined_date=datetime.date(2023, 3, 15),
        avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=200",
        role="Teacher"
    )

    t2 = Teacher.objects.create(
        username="rajesh.kumar",
        name="Rajesh Kumar",
        email="rajesh.k@ngoteach.org",
        school_region="Bihar Community Learning Hub",
        subject_specialty="General Science & Physics",
        joined_date=datetime.date(2022, 11, 4),
        avatar="https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=200",
        role="Teacher"
    )

    t3 = Teacher.objects.create(
        username="sunita.patel",
        name="Sunita Patel",
        email="sunita.patel@ngoteach.org",
        school_region="Gujarat Tribal Belt Primary",
        subject_specialty="English Communication",
        joined_date=datetime.date(2024, 1, 10),
        avatar="https://images.unsplash.com/photo-1580894732413-80c8509c2794?auto=format&fit=crop&q=80&w=200",
        role="Teacher"
    )

    # Admin User Profile
    admin_user = Teacher.objects.create(
        username="admin",
        password="adminpassword",
        name="Dr. Aris Thorne (Program Lead)",
        email="admin@ngoteach.org",
        school_region="NGO Regional Directorate HQ",
        subject_specialty="Curriculum Operations",
        joined_date=datetime.date(2021, 1, 1),
        avatar="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=200",
        role="Admin"
    )

    admin_yashraj = Teacher.objects.create(
        username="Maverick",
        password="Yashraj@7777",
        name="Yashraj Bhogade",
        email="yashraj@sproughub.org",
        school_region="Sproug Hub Directorate HQ",
        subject_specialty="Platform Administrator",
        joined_date=datetime.date(2024, 1, 1),
        avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200",
        role="Admin"
    )

    # 2. Create Lessons
    l1 = Lesson.objects.create(
        title="Foundational Geometry & Spatial Reasoning",
        subject="Mathematics",
        grade="Grade 6",
        duration="40 mins",
        summary="An interactive lesson on two-dimensional geometric properties, area calculations, and spatial problem solving designed for rural classrooms with minimal equipment requirements.",
        thumbnail="https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&q=80&w=600"
    )

    LessonContent.objects.create(
        lesson=l1,
        title="Visualizing Triangles and Quadrilaterals",
        content_type="video",
        url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        description="Video demonstration using paper-folding techniques to discover geometric properties.",
        order=1
    )
    LessonContent.objects.create(
        lesson=l1,
        title="Classroom Geometry Worksheet & Guide",
        content_type="pdf",
        url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        description="Printable or offline viewable student activity sheets with real-world area calculation tasks.",
        order=2
    )
    LessonContent.objects.create(
        lesson=l1,
        title="Geometry Concepts Quick Check",
        content_type="quiz",
        url="https://example.com/quiz/geometry-basics",
        description="Self-assessment quiz for teachers to gauge student mastery during class.",
        order=3
    )

    l2 = Lesson.objects.create(
        title="Introduction to Ecosystems & Solar Energy",
        subject="Science",
        grade="Grade 7",
        duration="50 mins",
        summary="Explores food chains, photosynthesis, and how solar energy powers rural micro-ecosystems using simple local environmental observations.",
        thumbnail="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&q=80&w=600"
    )

    LessonContent.objects.create(
        lesson=l2,
        title="Photosynthesis & Energy Flow Video",
        content_type="video",
        url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        description="Animated visual walkthrough of sunlight conversion into chemical energy in local plant species.",
        order=1
    )
    LessonContent.objects.create(
        lesson=l2,
        title="Interactive Slide Deck: Food Webs",
        content_type="interactive",
        url="https://example.com/slides/food-webs",
        description="Slide presentation suitable for projector or tablet delivery.",
        order=2
    )

    l3 = Lesson.objects.create(
        title="English Reading Comprehension & Storytelling",
        subject="English",
        grade="Grade 5",
        duration="35 mins",
        summary="Enhances vocabulary acquisition and contextual listening through vernacular-assisted bilingual folk storytelling exercises.",
        thumbnail="https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=600"
    )

    LessonContent.objects.create(
        lesson=l3,
        title="Bilingual Storytelling Audio & Text",
        content_type="video",
        url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        description="Engaging narration with subtitle support to build English phonetic familiarity.",
        order=1
    )

    l4 = Lesson.objects.create(
        title="Basic Chemistry: States of Matter & Water Cycle",
        subject="Science",
        grade="Grade 8",
        duration="45 mins",
        summary="Demonstrates evaporation, condensation, and precipitation using simple water heating and cooling experiments in rural school labs.",
        thumbnail="https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&q=80&w=600"
    )

    LessonContent.objects.create(
        lesson=l4,
        title="Water Cycle Laboratory Demonstration",
        content_type="video",
        url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        description="Step-by-step experiment video showing phase changes using local pots and clear glass.",
        order=1
    )

    # 3. Assign Lessons to Teachers
    TeacherLessonAssignment.objects.create(
        teacher=t1,
        lesson=l1,
        completed=True,
        completed_content_ids=[]
    )
    TeacherLessonAssignment.objects.create(
        teacher=t1,
        lesson=l2,
        completed=False,
        completed_content_ids=[]
    )
    TeacherLessonAssignment.objects.create(
        teacher=t2,
        lesson=l2,
        completed=True,
        completed_content_ids=[]
    )
    TeacherLessonAssignment.objects.create(
        teacher=t2,
        lesson=l4,
        completed=False,
        completed_content_ids=[]
    )
    TeacherLessonAssignment.objects.create(
        teacher=t3,
        lesson=l3,
        completed=True,
        completed_content_ids=[]
    )

    # 4. Seed Audit Logs
    LoginHistory.objects.create(
        username="anita.sharma",
        user_role="Teacher",
        timestamp=timezone.now() - datetime.timedelta(hours=2),
        ip_address="192.168.1.102",
        status="Success"
    )
    LoginHistory.objects.create(
        username="admin",
        user_role="Admin",
        timestamp=timezone.now() - datetime.timedelta(hours=5),
        ip_address="10.0.0.1",
        status="Success"
    )

    print("Database successfully seeded with default records!")
