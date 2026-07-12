import { useMemo, useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

const resourceName = 'Conference Room'
const slotStartTimes = ['08:00', '09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00']

const initialBookings = [
  {
    id: 1,
    title: 'Leadership sync',
    start_time: '2026-07-12T09:00:00',
    end_time: '2026-07-12T10:00:00',
    status: 'upcoming',
    purpose: 'Discuss quarterly plan',
  },
  {
    id: 2,
    title: 'Design review',
    start_time: '2026-07-12T14:00:00',
    end_time: '2026-07-12T15:00:00',
    status: 'ongoing',
    purpose: 'Review wireframes',
  },
]

const buildSlot = (label) => {
  const [hour] = label.split(':')
  const startDate = new Date('2026-07-12T00:00:00')
  startDate.setHours(Number(hour), 0, 0, 0)
  const endDate = new Date(startDate)
  endDate.setHours(startDate.getHours() + 1)

  return {
    label,
    start_time: startDate.toISOString(),
    end_time: endDate.toISOString(),
  }
}

const slotDefinitions = slotStartTimes.map(buildSlot)

const BookingPage = () => {
  const [bookings, setBookings] = useState(initialBookings)
  const [selectedBookingId, setSelectedBookingId] = useState(initialBookings[0]?.id ?? null)
  const [form, setForm] = useState({
    start_time: slotDefinitions[0].start_time,
    end_time: slotDefinitions[0].end_time,
    purpose: '',
  })
  const [feedback, setFeedback] = useState('Choose a slot to create a booking or pick an existing booking to reschedule it.')

  const activeBookings = useMemo(() => bookings.filter((booking) => booking.status !== 'cancelled'), [bookings])

  const isSlotBooked = (slot) =>
    activeBookings.some((booking) => booking.start_time < slot.end_time && booking.end_time > slot.start_time)

  const handleCreate = (event) => {
    event.preventDefault()
    const exists = activeBookings.some(
      (booking) => booking.start_time < form.end_time && booking.end_time > form.start_time,
    )

    if (exists) {
      setFeedback('That slot overlaps with an existing booking. Choose a different time.')
      return
    }

    const newBooking = {
      id: Date.now(),
      title: form.purpose || 'New booking',
      start_time: form.start_time,
      end_time: form.end_time,
      status: 'upcoming',
      purpose: form.purpose,
    }

    setBookings((current) => [newBooking, ...current])
    setSelectedBookingId(newBooking.id)
    setFeedback('Booking created successfully.')
  }

  const handleCancel = (bookingId) => {
    setBookings((current) =>
      current.map((booking) => (booking.id === bookingId ? { ...booking, status: 'cancelled' } : booking)),
    )
    setFeedback('Booking cancelled.')
  }

  const handleReschedule = (bookingId) => {
    setBookings((current) =>
      current.map((booking) =>
        booking.id === bookingId ? { ...booking, start_time: form.start_time, end_time: form.end_time, status: 'upcoming' } : booking,
      ),
    )
    setFeedback('Booking rescheduled.')
  }

  return (
    <div className="min-h-screen bg-[#f5f5f5] px-4 py-8 text-[#333333] sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="space-y-2">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-[#008080]">Resource booking</p>
          <h1 className="text-3xl font-semibold text-[#333333]">{resourceName} calendar</h1>
          <p className="max-w-2xl text-sm text-[#666666]">
            Review availability for the day and create, cancel, or reschedule bookings without overlaps.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.45fr_0.8fr]">
          <Card title="Availability" className="bg-white">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {slotDefinitions.map((slot) => {
                const booked = isSlotBooked(slot)
                const selected = form.start_time === slot.start_time
                return (
                  <button
                    key={slot.label}
                    type="button"
                    onClick={() => {
                      setForm({ ...form, start_time: slot.start_time, end_time: slot.end_time })
                      setSelectedBookingId(null)
                      setFeedback(`Selected ${slot.label} for a new booking.`)
                    }}
                    className={`rounded-xl border p-4 text-left transition-colors ${
                      booked
                        ? 'border-[#008080] bg-[#008080] text-white'
                        : selected
                          ? 'border-[#008080] bg-[#f2fafa] text-[#333333]'
                          : 'border-gray-200 bg-[#f5f5f5] text-[#333333] hover:border-[#006666] hover:bg-[#006666] hover:text-white'
                    }`}
                  >
                    <div className="font-semibold">{slot.label}</div>
                    <div className="mt-2 text-sm">
                      {booked ? 'Booked' : 'Available'}
                    </div>
                  </button>
                )
              })}
            </div>
          </Card>

          <Card title="Booking details" className="bg-white">
            <form className="space-y-4" onSubmit={handleCreate}>
              <div>
                <label className="mb-1 block text-sm font-medium text-[#333333]">Start</label>
                <input
                  className="w-full rounded-md border border-gray-300 px-3 py-2"
                  type="datetime-local"
                  value={form.start_time.replace(':00.000Z', '').replace('T', 'T')}
                  onChange={(event) => setForm({ ...form, start_time: event.target.value })}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-[#333333]">End</label>
                <input
                  className="w-full rounded-md border border-gray-300 px-3 py-2"
                  type="datetime-local"
                  value={form.end_time.replace(':00.000Z', '').replace('T', 'T')}
                  onChange={(event) => setForm({ ...form, end_time: event.target.value })}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-[#333333]">Purpose</label>
                <input
                  className="w-full rounded-md border border-gray-300 px-3 py-2"
                  value={form.purpose}
                  onChange={(event) => setForm({ ...form, purpose: event.target.value })}
                  placeholder="Team meeting"
                />
              </div>
              <div className="flex flex-wrap gap-3">
                <Button type="submit" variant="primary">Create booking</Button>
                <Button type="button" variant="secondary" onClick={() => setForm({ start_time: slotDefinitions[0].start_time, end_time: slotDefinitions[0].end_time, purpose: '' })}>
                  Reset
                </Button>
              </div>
              <p className="text-sm text-[#666666]">{feedback}</p>
            </form>
          </Card>
        </div>

        <Card title="Upcoming bookings" className="bg-white">
          <div className="space-y-3">
            {activeBookings.map((booking) => (
              <div key={booking.id} className="flex flex-col gap-3 rounded-xl border border-gray-200 bg-[#f5f5f5] p-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="font-semibold text-[#333333]">{booking.title}</div>
                  <div className="text-sm text-[#666666]">{booking.purpose || 'No purpose provided'}</div>
                  <div className="mt-1 text-sm text-[#008080]">
                    {new Date(booking.start_time).toLocaleString()} → {new Date(booking.end_time).toLocaleString()}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button type="button" variant="outline" onClick={() => { setSelectedBookingId(booking.id); setForm({ start_time: booking.start_time, end_time: booking.end_time, purpose: booking.purpose || '' }); setFeedback('Rescheduling selected booking.'); }}>
                    Reschedule
                  </Button>
                  <Button type="button" variant="secondary" onClick={() => handleCancel(booking.id)}>
                    Cancel
                  </Button>
                  {selectedBookingId === booking.id ? (
                    <Button type="button" variant="primary" onClick={() => handleReschedule(booking.id)}>
                      Apply
                    </Button>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}

export default BookingPage
