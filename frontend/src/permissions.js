// Refleja la matriz de backend/accounts/permissions.py. Solo decide qué se muestra: la API es quien autoriza.
export const ROLE_LABELS = {
  administrator: 'Administrador',
  pastor: 'Pastor',
  secretary: 'Secretario(a)',
  treasurer: 'Tesorero(a)',
  coordinator: 'Coordinador(a)',
}

const LEADERSHIP = ['administrator', 'pastor', 'secretary']
const OPERATIONAL = [...LEADERSHIP, 'coordinator']

const CAPABILITIES = {
  'users.manage': ['administrator'],
  'members.manage': LEADERSHIP,
  'events.manage': OPERATIONAL,
  'events.assign': LEADERSHIP,
  'attendance.manage': OPERATIONAL,
  'ministries.manage': LEADERSHIP,
  'finances.manage': ['administrator', 'treasurer'],
  'finances.summary': ['administrator', 'treasurer', 'pastor'],
  'announcements.manage': LEADERSHIP,
  'reports.operational': LEADERSHIP,
  'church.manage': ['administrator'],
}

export function can(user, capability) {
  return CAPABILITIES[capability].includes(user.role)
}
