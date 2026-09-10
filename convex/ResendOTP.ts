import Resend from '@auth/core/providers/resend'

/**
 * Email one-time-password provider.
 *
 * If `AUTH_RESEND_KEY` is configured in the Convex deployment the code is
 * emailed via Resend. Otherwise (local / demo) the code is printed to the
 * Convex logs so you can still sign in.
 */
function generateOTP(length = 6): string {
  const digits = new Uint32Array(length)
  crypto.getRandomValues(digits)
  return Array.from(digits, (d) => (d % 10).toString()).join('')
}

export const ResendOTP = Resend({
  id: 'resend-otp',
  apiKey: process.env.AUTH_RESEND_KEY ?? 'dev-no-key',
  maxAge: 60 * 15,
  async generateVerificationToken() {
    return generateOTP(6)
  },
  async sendVerificationRequest({ identifier: email, token }) {
    const apiKey = process.env.AUTH_RESEND_KEY
    if (!apiKey) {
      // eslint-disable-next-line no-console
      console.info(
        `\n──────────────────────────────────────────────\n New Star Tailor sign-in code for ${email}: ${token}\n (Set AUTH_RESEND_KEY in Convex env for real emails.)\n──────────────────────────────────────────────\n`,
      )
      return
    }
    const from =
      process.env.AUTH_EMAIL_FROM ?? 'New Star Tailor <onboarding@resend.dev>'
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from,
        to: [email],
        subject: `${token} is your New Star Tailor sign-in code`,
        text: `Your New Star Tailor sign-in code is ${token}.\n\nIt is valid for 15 minutes. If you did not request this, you can ignore this email.`,
      }),
    })
    if (!res.ok) {
      throw new Error(`Could not send verification email: ${await res.text()}`)
    }
  },
})
