<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Support</h1>
        <p class="mt-2 text-sm text-gray-700">
          Get help and contact our support team
        </p>
      </div>
    </div>

    <div class="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
      <!-- Documentation -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Documentation</h3>
        <div class="space-y-4">
          <div class="flex items-center p-4 bg-gray-50 rounded-lg">
            <div class="flex-shrink-0">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
            <div class="ml-4">
              <h4 class="text-sm font-medium text-gray-900">User Guide</h4>
              <p class="text-sm text-gray-500">Learn how to use the platform</p>
            </div>
            <div class="ml-auto">
              <a href="#" class="text-primary-600 hover:text-primary-500 text-sm font-medium">
                View →
              </a>
            </div>
          </div>

          <div class="flex items-center p-4 bg-gray-50 rounded-lg">
            <div class="flex-shrink-0">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <h4 class="text-sm font-medium text-gray-900">API Documentation</h4>
              <p class="text-sm text-gray-500">Integrate with our APIs</p>
            </div>
            <div class="ml-auto">
              <a href="/api/v1/docs" class="text-primary-600 hover:text-primary-500 text-sm font-medium">
                View →
              </a>
            </div>
          </div>

          <div class="flex items-center p-4 bg-gray-50 rounded-lg">
            <div class="flex-shrink-0">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <h4 class="text-sm font-medium text-gray-900">FAQ</h4>
              <p class="text-sm text-gray-500">Frequently asked questions</p>
            </div>
            <div class="ml-auto">
              <a href="#" class="text-primary-600 hover:text-primary-500 text-sm font-medium">
                View →
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Support -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Contact Support</h3>
        <form @submit.prevent="handleSubmitTicket" class="space-y-4">
          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700">
              Subject
            </label>
            <input
              id="subject"
              v-model="ticketForm.subject"
              type="text"
              required
              class="input-field mt-1"
              placeholder="Brief description of your issue"
            />
          </div>
          <div>
            <label for="category" class="block text-sm font-medium text-gray-700">
              Category
            </label>
            <select id="category" v-model="ticketForm.category" required class="input-field mt-1">
              <option value="">Select a category</option>
              <option value="technical">Technical Issue</option>
              <option value="billing">Billing Question</option>
              <option value="feature">Feature Request</option>
              <option value="general">General Inquiry</option>
            </select>
          </div>
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="description"
              v-model="ticketForm.description"
              rows="4"
              required
              class="input-field mt-1"
              placeholder="Please provide detailed information about your issue..."
            ></textarea>
          </div>

          <div v-if="ticketError" class="text-red-600 text-sm">
            {{ ticketError }}
          </div>

          <div v-if="ticketSuccess" class="text-green-600 text-sm">
            {{ ticketSuccess }}
          </div>

          <button
            type="submit"
            :disabled="ticketLoading"
            class="btn-primary w-full"
          >
            {{ ticketLoading ? 'Submitting...' : 'Submit Ticket' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Contact Information -->
    <div class="mt-8">
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div class="text-center">
            <div class="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <h4 class="mt-2 text-sm font-medium text-gray-900">Email Support</h4>
            <p class="mt-1 text-sm text-gray-500">support@smartsecurity.solutions</p>
          </div>

          <div class="text-center">
            <div class="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
              </svg>
            </div>
            <h4 class="mt-2 text-sm font-medium text-gray-900">Phone Support</h4>
            <p class="mt-1 text-sm text-gray-500">+1 (555) 123-4567</p>
          </div>

          <div class="text-center">
            <div class="mx-auto w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
              </svg>
            </div>
            <h4 class="mt-2 text-sm font-medium text-gray-900">Live Chat</h4>
            <p class="mt-1 text-sm text-gray-500">Available 24/7</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const ticketForm = ref({
  subject: '',
  category: '',
  description: ''
})

const ticketLoading = ref(false)
const ticketError = ref('')
const ticketSuccess = ref('')

const handleSubmitTicket = async () => {
  ticketLoading.value = true
  ticketError.value = ''
  ticketSuccess.value = ''

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ticketSuccess.value = 'Support ticket submitted successfully! We will get back to you within 24 hours.'
    ticketForm.value = {
      subject: '',
      category: '',
      description: ''
    }
  } catch (error) {
    ticketError.value = 'Failed to submit ticket. Please try again.'
  } finally {
    ticketLoading.value = false
  }
}
</script> 