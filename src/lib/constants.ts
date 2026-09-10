export const ORDER_STATUSES = ['new', 'measurement', 'ready', 'delivered'] as const
export type OrderStatus = (typeof ORDER_STATUSES)[number]

export const PRIORITIES = ['normal', 'urgent'] as const
export type Priority = (typeof PRIORITIES)[number]

export const FABRIC_SOURCES = ['customer', 'shop'] as const
export type FabricSource = (typeof FABRIC_SOURCES)[number]

export const FITTING_PREFERENCES = ['slim', 'regular', 'relaxed'] as const
export type FittingPreference = (typeof FITTING_PREFERENCES)[number]

export const SERVICE_CATEGORIES = ['regular', 'police', 'crpf', 'army'] as const
export type ServiceCategory = (typeof SERVICE_CATEGORIES)[number]

export const PAYMENT_METHODS = ['cash', 'upi', 'online'] as const
export type PaymentMethod = (typeof PAYMENT_METHODS)[number]

/** The measurement fields prompted for in the admin UI, in display order. */
export const MEASUREMENT_FIELDS: Array<{
  key: string
  en: string
  hi: string
  group: 'upper' | 'lower'
}> = [
  { key: 'length', en: 'Length', hi: 'लंबाई', group: 'upper' },
  { key: 'shoulder', en: 'Shoulder', hi: 'कंधा', group: 'upper' },
  { key: 'chest', en: 'Chest', hi: 'छाती', group: 'upper' },
  { key: 'stomach', en: 'Stomach', hi: 'पेट', group: 'upper' },
  { key: 'seat', en: 'Seat / Hip', hi: 'कमर के नीचे (हिप)', group: 'upper' },
  { key: 'sleeve_length', en: 'Sleeve length', hi: 'आस्तीन की लंबाई', group: 'upper' },
  { key: 'sleeve_loose', en: 'Sleeve (loose)', hi: 'आस्तीन (ढीली)', group: 'upper' },
  { key: 'neck', en: 'Neck / Collar', hi: 'कॉलर', group: 'upper' },
  { key: 'front_cross', en: 'Front cross', hi: 'आगे की चौड़ाई', group: 'upper' },
  { key: 'back_cross', en: 'Back cross', hi: 'पीछे की चौड़ाई', group: 'upper' },
  { key: 'pant_length', en: 'Pant length', hi: 'पैंट की लंबाई', group: 'lower' },
  { key: 'waist', en: 'Waist', hi: 'कमर', group: 'lower' },
  { key: 'hip', en: 'Hip', hi: 'हिप', group: 'lower' },
  { key: 'thigh', en: 'Thigh', hi: 'जांघ', group: 'lower' },
  { key: 'knee', en: 'Knee', hi: 'घुटना', group: 'lower' },
  { key: 'pant_mori', en: 'Bottom (Mori)', hi: 'मोरी (पैंट का खुला हिस्सा)', group: 'lower' },
  { key: 'crotch', en: 'Crotch / Rise', hi: 'राइज़', group: 'lower' },
]
