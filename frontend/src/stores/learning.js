import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useLearningStore = defineStore('learning', () => {
  const records = ref([]);
  const progress = ref({});
  const collections = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const totalLearningHours = computed(() => {
    return records.value.reduce((sum, record) => sum + (record.duration || 0), 0) / 60;
  });

  const recentRecords = computed(() => {
    return [...records.value].sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    ).slice(0, 10);
  });

  async function fetchLearningRecords() {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/learning/records', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch learning records');
      }
      records.value = await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching learning records:', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchLearningProgress() {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/learning/progress', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch learning progress');
      }
      progress.value = await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching learning progress:', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchCollections() {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/learning/collections', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch collections');
      }
      collections.value = await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching collections:', err);
    } finally {
      loading.value = false;
    }
  }

  async function addCollection(knowledgePointId, note = '') {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/learning/collections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ 
          knowledge_point_id: knowledgePointId,
          note: note 
        })
      });
      if (!response.ok) {
        throw new Error('Failed to add collection');
      }
      await fetchCollections();
    } catch (err) {
      error.value = err.message;
      console.error('Error adding collection:', err);
    } finally {
      loading.value = false;
    }
  }

  async function removeCollection(collectionId) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`http://localhost:8000/api/learning/collections/${collectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to remove collection');
      }
      await fetchCollections();
    } catch (err) {
      error.value = err.message;
      console.error('Error removing collection:', err);
    } finally {
      loading.value = false;
    }
  }

  async function trackLearning(knowledgePointId, action, duration = 0) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/learning/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ 
          knowledge_point_id: knowledgePointId,
          action: action,
          duration: duration 
        })
      });
      if (!response.ok) {
        throw new Error('Failed to track learning');
      }
      await fetchLearningRecords();
    } catch (err) {
      error.value = err.message;
      console.error('Error tracking learning:', err);
    } finally {
      loading.value = false;
    }
  }

  return {
    records,
    progress,
    collections,
    loading,
    error,
    totalLearningHours,
    recentRecords,
    fetchLearningRecords,
    fetchLearningProgress,
    fetchCollections,
    addCollection,
    removeCollection,
    trackLearning
  };
});
