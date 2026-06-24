import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCourseStore = defineStore('course', () => {
  const courses = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const enrolledCourses = ref([]);

  const allCourses = computed(() => courses.value);
  const requiredCourses = computed(() => 
    courses.value.filter(c => c.course_type === 'required')
  );
  const electiveCourses = computed(() => 
    courses.value.filter(c => c.course_type === 'elective')
  );

  async function fetchCourses() {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/courses', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch courses');
      }
      courses.value = await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching courses:', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchEnrolledCourses() {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/learning/enrollments', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch enrolled courses');
      }
      enrolledCourses.value = await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching enrolled courses:', err);
    } finally {
      loading.value = false;
    }
  }

  async function enrollCourse(courseId) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/learning/enroll', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ course_id: courseId })
      });
      if (!response.ok) {
        throw new Error('Failed to enroll course');
      }
      await fetchEnrolledCourses();
    } catch (err) {
      error.value = err.message;
      console.error('Error enrolling course:', err);
    } finally {
      loading.value = false;
    }
  }

  async function getCourseById(courseId) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`http://localhost:8000/api/knowledge/courses/${courseId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch course');
      }
      return await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching course:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  return {
    courses,
    loading,
    error,
    enrolledCourses,
    allCourses,
    requiredCourses,
    electiveCourses,
    fetchCourses,
    fetchEnrolledCourses,
    enrollCourse,
    getCourseById
  };
});
