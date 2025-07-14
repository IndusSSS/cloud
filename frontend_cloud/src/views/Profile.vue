<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Profile</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage your account settings and preferences
        </p>
      </div>
    </div>

    <div class="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
      <!-- Profile Information -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
        <div v-if="authStore.user" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Username</label>
            <div class="mt-1 text-sm text-gray-900">{{ authStore.user.username }}</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <div class="mt-1 text-sm text-gray-900">{{ authStore.user.email }}</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Account Type</label>
            <div class="mt-1 text-sm text-gray-900">
              {{ authStore.user.is_admin ? 'Administrator' : 'Customer' }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Tenant ID</label>
            <div class="mt-1 text-sm text-gray-900">{{ authStore.user.tenant_id || 'N/A' }}</div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          Loading profile information...
        </div>
      </div>

      <!-- Change Password -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label for="current-password" class="block text-sm font-medium text-gray-700">
              Current Password
            </label>
            <input
              id="current-password"
              v-model="passwordForm.currentPassword"
              type="password"
              required
              class="input-field mt-1"
              placeholder="Enter current password"
            />
          </div>
          <div>
            <label for="new-password" class="block text-sm font-medium text-gray-700">
              New Password
            </label>
            <input
              id="new-password"
              v-model="passwordForm.newPassword"
              type="password"
              required
              class="input-field mt-1"
              placeholder="Enter new password"
            />
          </div>
          <div>
            <label for="confirm-password" class="block text-sm font-medium text-gray-700">
              Confirm New Password
            </label>
            <input
              id="confirm-password"
              v-model="passwordForm.confirmPassword"
              type="password"
              required
              class="input-field mt-1"
              placeholder="Confirm new password"
            />
          </div>

          <div v-if="passwordError" class="text-red-600 text-sm">
            {{ passwordError }}
          </div>

          <div v-if="passwordSuccess" class="text-green-600 text-sm">
            {{ passwordSuccess }}
          </div>

          <button
            type="submit"
            :disabled="passwordLoading"
            class="btn-primary w-full"
          >
            {{ passwordLoading ? 'Changing Password...' : 'Change Password' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Account Actions -->
    <div class="mt-8">
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Account Actions</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-medium text-gray-900">Export Data</h4>
              <p class="text-sm text-gray-500">Download your device data and settings</p>
            </div>
            <button class="btn-secondary">
              Export
            </button>
          </div>
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-medium text-gray-900">Delete Account</h4>
              <p class="text-sm text-gray-500">Permanently delete your account and all data</p>
            </div>
            <button class="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

const handleChangePassword = async () => {
  // Reset messages
  passwordError.value = ''
  passwordSuccess.value = ''

  // Validate passwords match
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = 'New passwords do not match'
    return
  }

  // Validate password length
  if (passwordForm.value.newPassword.length < 6) {
    passwordError.value = 'New password must be at least 6 characters long'
    return
  }

  passwordLoading.value = true

  try {
    const result = await authStore.changePassword(
      passwordForm.value.currentPassword,
      passwordForm.value.newPassword
    )

    if (result.success) {
      passwordSuccess.value = 'Password changed successfully'
      passwordForm.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    } else {
      passwordError.value = result.error
    }
  } catch (error) {
    passwordError.value = 'An error occurred while changing password'
  } finally {
    passwordLoading.value = false
  }
}

onMounted(async () => {
  await authStore.fetchProfile()
})
</script> 