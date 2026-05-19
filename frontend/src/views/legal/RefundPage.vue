<template>
  <div class="legal-page">
    <div class="legal-container">
      <a href="#" class="legal-back" @click.prevent="$router.back()">&larr; Back</a>
      <h1>Refund Policy</h1>
      <p class="legal-updated">Last updated: January 2026</p>

      <section>
        <h2>Eligibility for Refunds</h2>
        <p>Refunds are issued in the following circumstances:</p>
        <ul>
          <li>Cancellation within the applicable free cancellation window (see Cancellation Policy).</li>
          <li>Cook no-show or last-minute cancellation by the cook.</li>
          <li>Significant quality issues reported and verified within 2 hours of meal delivery.</li>
          <li>Safety concerns verified by our quality team.</li>
        </ul>
      </section>

      <section>
        <h2>Refund Process</h2>
        <p>To request a refund:</p>
        <ul>
          <li>Navigate to your booking detail page and select "Report Issue".</li>
          <li>Describe the issue and attach photos if applicable.</li>
          <li>Our support team will review within 24–48 hours.</li>
        </ul>
      </section>

      <section>
        <h2>Refund Amounts</h2>
        <ul>
          <li><strong>Cook no-show:</strong> 100% refund.</li>
          <li><strong>Quality issue (verified):</strong> Up to 100% refund at our discretion based on severity.</li>
          <li><strong>Partial delivery:</strong> Proportional refund for items not received.</li>
          <li><strong>Customer cancellation:</strong> Refund as per Cancellation Policy tiers.</li>
        </ul>
      </section>

      <section>
        <h2>Refund Timeline</h2>
        <p>Approved refunds are processed within 5–7 business days. The amount will be credited back to the original payment method. Bank processing times may add 2–3 additional days.</p>
      </section>

      <section>
        <h2>Non-Refundable Cases</h2>
        <ul>
          <li>Customer no-show without prior cancellation.</li>
          <li>Minor variations in presentation from menu photos.</li>
          <li>Complaints filed more than 24 hours after the booking.</li>
          <li>Taste preferences (unless a specific dish was ordered and a different one was delivered).</li>
        </ul>
      </section>

      <section>
        <h2>Contact</h2>
        <p>For refund queries, email <strong>support@sizzzle.me</strong> or use in-app support.</p>
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
