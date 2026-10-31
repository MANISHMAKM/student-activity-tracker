import { useEffect, useState } from 'react'
import { addActivity, deleteActivity, getActivities, getErrorMessage, getSummary } from './api'
import ActivityForm from './components/ActivityForm'
import ActivityList from './components/ActivityList'
import Summary from './components/Summary'

function App() {
  const [activities, setActivities] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // get the activities and the summary from the backend
  async function loadData() {
    try {
      const activitiesResponse = await getActivities()
      const summaryResponse = await getSummary()
      setActivities(activitiesResponse.data)
      setSummary(summaryResponse.data)
      setError('')
    } catch (err) {
      setError(getErrorMessage(err))
    }
    setLoading(false)
  }

  // runs one time when the page opens
  useEffect(() => {
    loadData()
  }, [])

  // called from the form. Returns an error message, or an empty string if it worked
  async function handleAdd(newActivity) {
    try {
      await addActivity(newActivity)
      await loadData()
      return ''
    } catch (err) {
      return getErrorMessage(err)
    }
  }

  async function handleDelete(id) {
    const sure = window.confirm('Do you want to delete this activity?')
    if (!sure) {
      return
    }
    try {
      await deleteActivity(id)
      await loadData()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>Student Activity Tracker</h1>
        <p className="muted">Add student activities and see how many hours they spend.</p>
      </header>

      {error && (
        <div className="alert" role="alert">
          <span>{error}</span>
          <button className="btn small" onClick={loadData}>
            Retry
          </button>
        </div>
      )}

      <div className="layout">
        <ActivityForm onAdd={handleAdd} />
        <div className="right">
          <Summary summary={summary} loading={loading} />
          <ActivityList activities={activities} loading={loading} onDelete={handleDelete} />
        </div>
      </div>
    </div>
  )
}

export default App
