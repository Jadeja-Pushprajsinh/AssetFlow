import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

const kpiCards = [
  { label: 'Available assets', value: '0', detail: 'ready for allocation' },
  { label: 'Allocated assets', value: '0', detail: 'currently assigned' },
  { label: 'Under maintenance', value: '0', detail: 'needs follow-up' },
  { label: 'Active bookings', value: '0', detail: 'this week' },
  { label: 'Pending transfers', value: '0', detail: 'awaiting review' },
  { label: 'Upcoming returns', value: '0', detail: 'within 7 days' },
]

const quickActions = ['Register asset', 'Create booking', 'Review maintenance', 'Approve transfer']

const DashboardPage = () => {
  return (
    <div className="min-h-screen bg-[#f5f5f5] px-4 py-8 text-[#333333] sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="space-y-2">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-[#008080]">Operations overview</p>
          <h1 className="text-3xl font-semibold text-[#333333]">Dashboard</h1>
          <p className="max-w-2xl text-sm text-[#666666]">
            A lightweight shell for the next layer of AssetFlow workflows, including asset health, bookings, and maintenance signals.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {kpiCards.map((card) => (
            <Card key={card.label} title={card.label} className="bg-[#fefefe]">
              <div className="space-y-2">
                <div className="text-3xl font-semibold text-[#008080]">{card.value}</div>
                <p className="text-sm text-[#666666]">{card.detail}</p>
              </div>
            </Card>
          ))}
        </section>

        <section className="overflow-hidden rounded-xl border border-[#aeeeee] bg-[#f2fafa] p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-[#333333]">Overdue items</h2>
              <p className="text-sm text-[#666666]">This section will soon list overdue allocations and follow-up actions.</p>
            </div>
            <div className="rounded-full bg-[#008080] px-3 py-1 text-sm font-medium text-white">Placeholder</div>
          </div>
        </section>

        <section className="space-y-3 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-[#333333]">Quick actions</h2>
              <p className="text-sm text-[#666666]">Common next steps for the team.</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            {quickActions.map((action) => (
              <Button key={action} variant="primary">
                {action}
              </Button>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

export default DashboardPage
