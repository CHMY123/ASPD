import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useBookStore = defineStore('book', () => {
  const books = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const categories = ref([]);
  const searchQuery = ref('');
  const selectedCategory = ref('');

  const filteredBooks = computed(() => {
    let result = books.value;
    
    if (selectedCategory.value) {
      result = result.filter(b => b.category === selectedCategory.value);
    }
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(b => 
        b.title.toLowerCase().includes(query) ||
        b.author.toLowerCase().includes(query)
      );
    }
    
    return result;
  });

  const groupedBooks = computed(() => {
    const groups = {};
    books.value.forEach(book => {
      const category = book.category || '其他';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(book);
    });
    return groups;
  });

  async function fetchBooks() {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/books', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch books');
      }
      books.value = await response.json();
      extractCategories();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching books:', err);
    } finally {
      loading.value = false;
    }
  }

  function extractCategories() {
    const cats = [...new Set(books.value.map(b => b.category || '其他'))];
    categories.value = cats;
  }

  async function getBookById(bookId) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`http://localhost:8000/api/knowledge/books/${bookId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch book');
      }
      return await response.json();
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching book:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  function setSearchQuery(query) {
    searchQuery.value = query;
  }

  function setCategory(category) {
    selectedCategory.value = category;
  }

  return {
    books,
    loading,
    error,
    categories,
    searchQuery,
    selectedCategory,
    filteredBooks,
    groupedBooks,
    fetchBooks,
    getBookById,
    setSearchQuery,
    setCategory
  };
});
