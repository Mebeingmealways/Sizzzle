import { ref } from 'vue'
import { notificationApi } from '../services/api'

const items = ref([])
const unreadCount = ref(0)
const loading = ref(false)
let pollTimer = null

async function refreshNotifications(limit = 10) {
  try {
    loading.value = true
    const data = await notificationApi.list(limit)
    items.value = data.items || []
    unreadCount.value = data.unread_count || 0
  } catch {
    // Keep UI stable if notifications fail.
  } finally {
    loading.value = false
  }
}

async function markRead(notificationId) {
  try {
    await notificationApi.markRead(notificationId)
    const current = items.value.find(i => i.id === notificationId)
    if (current && !current.is_read) {
      current.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  } catch {
    // Ignore transient network errors.
  }
}

async function markAllRead() {
  try {
    await notificationApi.markAllRead()
    items.value = items.value.map(i => ({ ...i, is_read: true }))
    unreadCount.value = 0
  } catch {
    // Ignore transient network errors.
  }
}

function startPolling(intervalMs = 12000) {
  stopPolling()
  pollTimer = setInterval(() => {
    refreshNotifications()
  }, intervalMs)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

export function useNotifications() {
  return {
    items,
    unreadCount,
    loading,
    refreshNotifications,
    markRead,
    markAllRead,
    startPolling,
    stopPolling,
  }
}
