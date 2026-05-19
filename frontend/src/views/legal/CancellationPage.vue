<template>
  <div class="legal-page">
    <div class="legal-container">
      <a href="#" class="legal-back" @click.prevent="$router.back()">&larr; Back</a>
      <h1>Cancellation Policy</h1>
      <p class="legal-updated">Last updated: January 2026</p>

      <section>
        <h2>For Customers</h2>
        <p>We understand plans change. Our cancellation tiers are designed to be fair to both customers and cooks:</p>
        <ul>
          <li><strong>12+ hours before booking:</strong> Full refund, no charges.</li>
          <li><strong>6–12 hours before booking:</strong> 80% refund. A small fee compensates the cook for reserved time.</li>
          <li><strong>2–6 hours before booking:</strong> 50% refund.</li>
          <li><strong>Less than 2 hours:</strong> No refund. The cook has likely already begun preparation.</li>
        </ul>
      </section>

      <section>
        <h2>For Cooks</h2>
        <p>Cooks who need to cancel accepted bookings should do so as early as possible:</p>
        <ul>
          <li><strong>24+ hours before:</strong> No penalty. Customer receives full refund.</li>
          <li><strong>12–24 hours before:</strong> Warning issued. Customer receives full refund.</li>
          <li><strong>Less than 12 hours:</strong> Penalty applied to cook's account. Repeated late cancellations may affect account standing.</li>
        </ul>
      </section>

      <section>
        <h2>Emergency Cancellations</h2>
        <p>In case of genuine emergencies (medical, natural disaster, etc.), both parties can request a review. Contact support with relevant details for case-by-case resolution.</p>
      </section>

      <section>
        <h2>No-Shows</h2>
        <p>If a customer is not available at the booking time and location, the cook may mark the booking as a no-show after a 30-minute wait. No refund will be issued.</p>
        <p>If a cook does not arrive, the customer will receive a full refund and the cook's account will be reviewed.</p>
      </section>

      <section>
        <h2>Contact</h2>
        <p>For cancellation-related queries, reach us at <strong>support@sizzzle.me</strong></p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.legal-page { min-height: 100vh; background: var(--bg); padding: 40px 20px 80px; }
.legal-container { max-width: 720px; margin: 0 auto; font-family: 'Inter', sans-serif; color: var(--text); }
.legal-back { display: inline-block; margin-bottom: 24px; color: var(--primary, #2DB67D); text-decoration: none; font-weight: 600; font-size: 0.9rem; }
.legal-back:hover { text-decoration: underline; }
h1 { font-size: 2rem; font-weight: 800; margin-bottom: 4px; }
.legal-updated { font-size: 0.82rem; opacity: 0.5; margin-bottom: 32px; }
section { margin-bottom: 28px; }
h2 { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; }
p { line-height: 1.7; font-size: 0.95rem; opacity: 0.85; }
ul { padding-left: 20px; margin-top: 8px; }
li { line-height: 1.7; font-size: 0.95rem; opacity: 0.85; margin-bottom: 4px; }
</style>
