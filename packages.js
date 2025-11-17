const PACKAGE_SOURCES = [
  { key: 'dnf', label: 'dnf' }, { key: 'pip', label: 'pip' },
  { key: 'npm', label: 'npm' }, { key: 'flatpak', label: 'flatpak' }
]
class PackagesWidget {
  async init (container, config = {}) {
    this.config = { refresh_seconds: 5, ...config }
    this.container = container
    this.pollTimer = null
    const template = await fetch('widgets/packages/packages.html').then(r => r.text())
    container.innerHTML = template
    window.monitor?.applyWidgetHeader?.(container, {
      suppressHeader: this.config._suppressHeader,
      name: this.config.name
    })
    this.countsEl = container.querySelector('[data-role="counts"]')
    this.metaEl = container.querySelector('[data-role="meta"]')
    try {
      await this.load()
      const refreshed = await this.load(true)
      if (refreshed.updating && !this.pollTimer) {
        const seconds = Number(refreshed.refresh_seconds || this.config.refresh_seconds || 5)
        const interval = Number.isFinite(seconds) && seconds > 0 ? seconds * 1000 : 5000
        this.pollTimer = window.setInterval(() => {
          this.load().catch(error => this.handleError(error))
        }, interval)
      }
    } catch (error) {
      this.handleError(error)
    }
  }
  async load (refresh = false) {
    const url = refresh ? 'api/system-packages?refresh=1' : 'api/system-packages'
    const response = await fetch(url, { cache: 'no-store' })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const payload = await response.json()
    this.render(payload)
    return payload
  }
  render (payload) {
    const cards = PACKAGE_SOURCES.map(({ key, label }) => {
      const info = payload.packages?.[key] || {}
      const value = typeof info.count === 'number' ? info.count : '—'
      const status = info.error || 'Healthy'
      const cardClass = info.error ? 'package-card is-error' : 'package-card'
      return `<div class="${cardClass}" data-source="${key}" title="${status}"><span class="package-name">${label}</span><span class="package-count">${value}</span><span class="package-status">${status}</span></div>`
    }).join('')
    this.countsEl.innerHTML = cards

    const updated = payload.updated
    if (payload.updating) {
      this.metaEl.textContent = updated
        ? `Refreshing… Last updated ${formatTimestamp(updated)}`
        : 'Refreshing…'
    } else if (updated) {
      this.metaEl.textContent = `Last updated ${formatTimestamp(updated)}`
      if (this.pollTimer) {
        window.clearInterval(this.pollTimer)
        this.pollTimer = null
      }
    } else {
      this.metaEl.textContent = 'Waiting for first refresh…'
    }
  }
  handleError (error) {
    const message = error instanceof Error ? error.message : String(error)
    this.metaEl.textContent = `Unable to load package data: ${message}`
  }
}
function formatTimestamp (value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}
window.widgets = window.widgets || {}
window.widgets.packages = PackagesWidget
