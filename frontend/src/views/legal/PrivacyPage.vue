<template>
  <div class="legal-page">
    <div class="legal-container">
      <a href="#" class="legal-back" @click.prevent="$router.back()">&larr; Back</a>
      <h1>Privacy Policy</h1>
      <p class="legal-updated">Last updated: January 2026</p>

      <section>
        <h2>1. Information We Collect</h2>
        <p>We collect information you provide directly when creating an account, making bookings, or contacting support:</p>
        <ul>
          <li><strong>Account Information:</strong> Name, email, phone number, and profile photo.</li>
          <li><strong>Booking Data:</strong> Addresses, dietary preferences, allergies, and meal selections.</li>
          <li><strong>Payment Information:</strong> Processed securely by our payment partners. We do not store full card details.</li>
          <li><strong>Usage Data:</strong> Pages visited, features used, and device information for improving the Service.</li>
        </ul>
      </section>

      <section>
        <h2>2. How We Use Your Information</h2>
        <ul>
          <li>To facilitate bookings between customers and cooks.</li>
          <li>To process payments and send receipts.</li>
          <li>To send booking confirmations, updates, and reminders.</li>
          <li>To improve the platform experience and develop new features.</li>
          <li>To ensure safety and prevent fraud.</li>
        </ul>
      </section>

      <section>
        <h2>3. Data Sharing</h2>
        <p>We share your information only as necessary:</p>
        <ul>
          <li><strong>Between parties:</strong> Cook name and customer address are shared to fulfill bookings.</li>
          <li><strong>Payment processors:</strong> To complete transactions securely.</li>
          <li><strong>Legal compliance:</strong> When required by law or to protect rights and safety.</li>
        </ul>
        <p>We never sell your personal data to third parties.</p>
      </section>

      <section>
        <h2>4. Data Security</h2>
        <p>We implement industry-standard security measures including encryption in transit and at rest, access controls, and regular security reviews to protect your data.</p>
      </section>

      <section>
        <h2>5. Your Rights</h2>
        <p>You may request access to, correction of, or deletion of your personal data at any time by contacting us. You can also update most of your information directly through your profile settings.</p>
      </section>

      <section>
        <h2>6. Cookies</h2>
        <p>We use essential cookies for authentication and session management. Analytics cookies are used to understand usage patterns and improve the Service. You can manage cookie preferences in your browser settings.</p>
      </section>

      <section>
        <h2>7. Contact</h2>
        <p>For privacy-related inquiries, contact our Data Protection team at <strong>privacy@sizzzle.me</strong></p>
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
