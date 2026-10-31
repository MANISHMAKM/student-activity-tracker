import { useState } from 'react'

function ActivityForm({ onAdd }) {
  const [name, setName] = useState('')
  const [activity, setActivity] = useState('')
  const [hours, setHours] = useState('')
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // basic validation before sending to the backend
  function validate() {
    const newErrors = {}

    if (name.trim() === '') {
      newErrors.name = 'Name is required.'
    }
    if (activity.trim() === '') {
      newErrors.activity = 'Activity is required.'
    }
    if (hours === '' || isNaN(Number(hours))) {
      newErrors.hours = 'Hours must be a number.'
    } else if (Number(hours) <= 0) {
      newErrors.hours = 'Hours must be greater than 0.'
    } else if (Number(hours) > 24) {
      newErrors.hours = 'Hours cannot be more than 24.'
    }

    return newErrors
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setServerError('')

    const newErrors = validate()
    setErrors(newErrors)
    if (Object.keys(newErrors).length > 0) {
      return
    }

    setSubmitting(true)
    const message = await onAdd({
      name: name.trim(),
      activity: activity.trim(),
      hours: Number(hours),
    })
    setSubmitting(false)

    if (message === '') {
      // success, clear the form
      setName('')
      setActivity('')
      setHours('')
    } else {
      setServerError(message)
    }
  }

  return (
    <form className="card form" onSubmit={handleSubmit} noValidate>
      <h2>Add Activity</h2>

      <div className="field">
        <label htmlFor="name">Student name</label>
        <input
          id="name"
          type="text"
          placeholder="e.g. Asha"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {errors.name && <span className="field-error">{errors.name}</span>}
      </div>

      <div className="field">
        <label htmlFor="activity">Activity</label>
        <input
          id="activity"
          type="text"
          placeholder="e.g. Football practice"
          value={activity}
          onChange={(e) => setActivity(e.target.value)}
        />
        {errors.activity && <span className="field-error">{errors.activity}</span>}
      </div>

      <div className="field">
        <label htmlFor="hours">Hours</label>
        <input
          id="hours"
          type="number"
          step="0.25"
          placeholder="e.g. 1.5"
          value={hours}
          onChange={(e) => setHours(e.target.value)}
        />
        {errors.hours && <span className="field-error">{errors.hours}</span>}
      </div>

      {serverError && (
        <div className="alert" role="alert">
          {serverError}
        </div>
      )}

      <button type="submit" className="btn primary" disabled={submitting}>
        {submitting ? 'Adding...' : 'Add Activity'}
      </button>
    </form>
  )
}

export default ActivityForm
