import { computed, onUnmounted, ref } from 'vue'

const EARTH_RADIUS_KM = 6371

function toRadians(value) {
  return (value * Math.PI) / 180
}

function getDistanceKm(from, to) {
  if (!from || !to) return null

  const dLat = toRadians(to.lat - from.lat)
  const dLon = toRadians(to.lng - from.lng)
  const lat1 = toRadians(from.lat)
  const lat2 = toRadians(to.lat)

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) * Math.sin(dLon / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return EARTH_RADIUS_KM * c
}

function formatDistance(distanceKm) {
  if (distanceKm == null) return 'Unknown'
  if (distanceKm < 1) return `${Math.round(distanceKm * 1000)} m`
  return `${distanceKm.toFixed(1)} km`
}

function estimateEta(distanceKm, averageSpeedKmh = 28) {
  if (distanceKm == null) return 'Unknown'
  const etaMinutes = Math.max(2, Math.round((distanceKm / averageSpeedKmh) * 60))
  return `${etaMinutes} min`
}

export function useLiveLocation(destination = null) {
  const permission = ref('prompt')
  const position = ref(null)
  const error = ref('')
  const loading = ref(false)
  const watching = ref(false)
  const updatedAt = ref(null)

  let watchId = null

  const destinationPosition = computed(() => destination?.value || destination || null)

  const distanceKm = computed(() => {
    return getDistanceKm(position.value, destinationPosition.value)
  })

  const distanceLabel = computed(() => formatDistance(distanceKm.value))
  const etaLabel = computed(() => estimateEta(distanceKm.value))

  function normalizePosition(geoPosition) {
    return {
      lat: geoPosition.coords.latitude,
      lng: geoPosition.coords.longitude,
      accuracy: Math.round(geoPosition.coords.accuracy || 0),
      heading: geoPosition.coords.heading,
      speed: geoPosition.coords.speed,
      timestamp: geoPosition.timestamp
    }
  }

  function handleSuccess(geoPosition) {
    position.value = normalizePosition(geoPosition)
    updatedAt.value = new Date()
    error.value = ''
    loading.value = false
  }

  function handleError(geoError) {
    loading.value = false

    if (geoError?.code === 1) {
      permission.value = 'denied'
      watching.value = false
      if (watchId != null) {
        navigator.geolocation.clearWatch(watchId)
        watchId = null
      }
      error.value = 'Location permission denied. Enable GPS access to use live tracking.'
      return
    }

    if (geoError?.code === 2) {
      error.value = 'Unable to determine your location right now. Try moving to an open area.'
      return
    }

    if (geoError?.code === 3) {
      error.value = 'Location request timed out. Please retry.'
      return
    }

    error.value = geoError?.message || 'Unable to fetch your location.'
  }

  function queryPermission() {
    if (!navigator?.permissions?.query) return

    navigator.permissions
      .query({ name: 'geolocation' })
      .then((result) => {
        permission.value = result.state
        result.onchange = () => {
          permission.value = result.state
        }
      })
      .catch(() => {})
  }

  function fetchCurrentPosition() {
    if (!navigator?.geolocation) {
      error.value = 'Geolocation is not supported in this browser.'
      return
    }

    loading.value = true
    navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
      enableHighAccuracy: true,
      timeout: 12000,
      maximumAge: 0
    })
  }

  function startWatching() {
    if (!navigator?.geolocation) {
      error.value = 'Geolocation is not supported in this browser.'
      return
    }

    if (permission.value === 'denied') {
      error.value = 'Location permission denied. Enable GPS access to use live tracking.'
      watching.value = false
      return
    }

    if (watchId != null) return

    loading.value = true
    watching.value = true

    watchId = navigator.geolocation.watchPosition(handleSuccess, handleError, {
      enableHighAccuracy: true,
      timeout: 12000,
      maximumAge: 1500
    })
  }

  function stopWatching() {
    if (watchId == null) return

    navigator.geolocation.clearWatch(watchId)
    watchId = null
    watching.value = false
  }

  function openMaps(from = position.value, to = destinationPosition.value) {
    if (!to) return

    const destinationQuery = `${to.lat},${to.lng}`
    const originQuery = from ? `${from.lat},${from.lng}` : null
    const mapsUrl = originQuery
      ? `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(originQuery)}&destination=${encodeURIComponent(destinationQuery)}&travelmode=driving`
      : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(destinationQuery)}`

    window.open(mapsUrl, '_blank', 'noopener,noreferrer')
  }

  queryPermission()

  onUnmounted(() => {
    stopWatching()
  })

  return {
    permission,
    position,
    destinationPosition,
    distanceKm,
    distanceLabel,
    etaLabel,
    error,
    loading,
    watching,
    updatedAt,
    fetchCurrentPosition,
    startWatching,
    stopWatching,
    openMaps,
    getDistanceKm,
    formatDistance,
    estimateEta
  }
}
