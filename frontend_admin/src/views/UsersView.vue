<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
            <p class="mt-1 text-sm text-gray-500">
              Manage system users and their permissions
            </p>
          </div>
          <button
            @click="showCreateModal = true"
            class="btn-primary"
          >
            Add User
          </button>
        </div>
      </div>
    </div>

    <!-- Users List -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div v-if="loading" class="flex justify-center py-8">
          <svg class="animate-spin h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <div v-else-if="error" class="text-center py-8">
          <div class="text-red-600">{{ error }}</div>
          <button @click="fetchUsers" class="btn-secondary mt-4">Retry</button>
        </div>
        <div v-else>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="user in users" :key="user.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                          <span class="text-sm font-medium text-indigo-600">
                            {{ user.username.charAt(0).toUpperCase() }}
                          </span>
                        </div>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ user.username }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">{{ user.email }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      ]"
                    >
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        user.is_admin
                          ? 'bg-purple-100 text-purple-800'
                          : 'bg-gray-100 text-gray-800'
                      ]"
                    >
                      {{ user.is_admin ? 'Admin' : 'User' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(user.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      @click="editUser(user)"
                      class="text-indigo-600 hover:text-indigo-900 mr-4"
                    >
                      Edit
                    </button>
                    <button
                      @click="deleteUser(user.id)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Create New User</h3>
          <form @submit.prevent="createUser">
            <div class="space-y-4">
              <div>
                <label class="form-label">Username</label>
                <input v-model="newUser.username" type="text" required class="form-input" />
              </div>
              <div>
                <label class="form-label">Email</label>
                <input v-model="newUser.email" type="email" required class="form-input" />
              </div>
              <div>
                <label class="form-label">Password</label>
                <input v-model="newUser.password" type="password" required class="form-input" />
              </div>
              <div>
                <label class="form-label">Tenant</label>
                <select v-model="newUser.tenant_id" required class="form-input">
                  <option value="" disabled>Select tenant</option>
                  <option v-for="tenant in tenants" :key="tenant.id" :value="tenant.id">
                    {{ tenant.name }}
                  </option>
                </select>
                <div v-if="tenantsLoading" class="text-xs text-gray-500 mt-1">Loading tenants...</div>
                <div v-if="tenantsError" class="text-xs text-red-500 mt-1">{{ tenantsError }}</div>
              </div>
              <div class="flex items-center">
                <input v-model="newUser.is_admin" type="checkbox" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" />
                <label class="ml-2 block text-sm text-gray-900">Admin privileges</label>
              </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="showCreateModal = false" class="btn-secondary">Cancel</button>
              <button type="submit" :disabled="creating" class="btn-primary">{{ creating ? 'Creating...' : 'Create User' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

export default {
  name: 'UsersView',
  setup() {
    const authStore = useAuthStore()
    const loading = ref(true)
    const creating = ref(false)
    const error = ref(null)
    const users = ref([])
    const showCreateModal = ref(false)
    const newUser = ref({
      username: '',
      email: '',
      password: '',
      is_admin: false,
      tenant_id: ''
    })
    const tenants = ref([])
    const tenantsLoading = ref(false)
    const tenantsError = ref(null)

    const fetchUsers = async () => {
      try {
        loading.value = true
        error.value = null
        
        const response = await fetch(`/api/v1/admin/users`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json',
          },
        })

        if (!response.ok) {
          const errorText = await response.text()
          console.error('Fetch users error response:', response.status, errorText)
          throw new Error(`Failed to fetch users: ${response.status}`)
        }

        const data = await response.json()
        users.value = data
      } catch (err) {
        error.value = err.message
        console.error('Error fetching users:', err)
      } finally {
        loading.value = false
      }
    }

    const createUser = async () => {
      try {
        creating.value = true
        if (!newUser.value.tenant_id) {
          error.value = 'Tenant is required.'
          creating.value = false
          return
        }
        
        console.log('Creating user with data:', newUser.value)
        
        const response = await fetch(`/api/v1/admin/users`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newUser.value),
        })

        console.log('Create user response status:', response.status)
        
        if (!response.ok) {
          const errorData = await response.json()
          console.error('Create user error response:', errorData)
          throw new Error(errorData.detail || `Failed to create user: ${response.status}`)
        }

        const result = await response.json()
        console.log('User created successfully:', result)

        // Reset form and close modal
        newUser.value = {
          username: '',
          email: '',
          password: '',
          is_admin: false,
          tenant_id: ''
        }
        showCreateModal.value = false
        
        // Refresh users list
        await fetchUsers()
      } catch (err) {
        error.value = err.message
        console.error('Error creating user:', err)
      } finally {
        creating.value = false
      }
    }

    const editUser = (user) => {
      // TODO: Implement edit functionality
      console.log('Edit user:', user)
    }

    const deleteUser = async (userId) => {
      if (!confirm('Are you sure you want to delete this user?')) {
        return
      }

      try {
        const response = await fetch(`/api/v1/admin/users/${userId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json',
          },
        })

        if (!response.ok) {
          throw new Error('Failed to delete user')
        }

        // Refresh users list
        await fetchUsers()
      } catch (err) {
        error.value = err.message
        console.error('Error deleting user:', err)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const fetchTenants = async () => {
      try {
        tenantsLoading.value = true
        tenantsError.value = null
        const response = await fetch(`/api/v1/admin/tenants`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json',
          },
        })
        if (!response.ok) {
          const errorText = await response.text()
          console.error('Fetch tenants error response:', response.status, errorText)
          throw new Error(`Failed to fetch tenants: ${response.status}`)
        }
        tenants.value = await response.json()
        console.log('Tenants loaded:', tenants.value)
      } catch (err) {
        tenantsError.value = err.message
        console.error('Error fetching tenants:', err)
      } finally {
        tenantsLoading.value = false
      }
    }

    onMounted(() => {
      fetchUsers()
      fetchTenants()
    })

    return {
      loading,
      creating,
      error,
      users,
      showCreateModal,
      newUser,
      fetchUsers,
      createUser,
      editUser,
      deleteUser,
      formatDate,
      tenants,
      tenantsLoading,
      tenantsError
    }
  }
}
</script> 