import axios from 'axios'

// address of the Flask backend
const API = axios.create({
  baseURL: 'http://127.0.0.1:5000',
})

export function getActivities() {
  return API.get('/activities')
}

export function getSummary() {
  return API.get('/summary')
}

export function addActivity(data) {
  return API.post('/activities', data)
}

export function deleteActivity(id) {
  return API.delete(`/activities/${id}`)
}

// turns an axios error into a message we can show on the screen
export function getErrorMessage(error) {
  if (error.response && error.response.data) {
    const data = error.response.data
    if (data.details) {
      return Object.values(data.details).join(' ')
    }
    if (data.error) {
      return data.error
    }
  }
  return 'Cannot connect to the server. Please check that the backend is running.'
}
