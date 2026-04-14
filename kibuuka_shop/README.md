

### What I Built
I  built a **mobile-first digital shop management system** for Kibuuka's Corner Shop — a real, working web application that replaces the paper notebooks, mental bookkeeping, and guesswork that small shops in Kampala rely on every day.

It runs in any browser, works on low-end Android phones, and requires no internet after the first setup — just a Wi-Fi router in the shop connecting phones to the server.

### The Pages and Why Each One Exists

**1. Login Page**
Two-panel design. The owner and assistants each have separate accounts. The system knows who is who — an assistant cannot touch credit records or delete products. This solves the real pain point of **unauthorized changes** in small shops.

**2. Dashboard**
The owner opens the app in the morning and immediately sees: today's revenue, how many sales happened, which items are running low, and how much money customers owe in credit — all in one glance. No digging through notebooks. This is the **command center**.

**3. Inventory / Products**
Every product has a buying price, selling price, unit, category, and a low-stock threshold. When stock drops below that threshold, a warning badge appears on the topbar automatically. The system tracks **profit margin per product** so Kibuuka always knows what's making money and what isn't.

**4. Add Stock (Restock)**
Every time stock is added, it records: who added it, what the buying price was that day, and which supplier. This builds a **restock history** — if prices go up with a supplier, Kibuuka has evidence to negotiate.

**5. Record Sale**
The assistant picks a product, enters quantity, chooses Cash, Mobile Money, or Credit. The system automatically deducts from stock, records who made the sale, and if it's Cash or Mobile Money, immediately opens a **printable receipt**. Credit sales are blocked from getting a receipt — as requested.

**6. Sales History**
A full ledger of every transaction with filters by date and payment method. The owner can see exactly what happened on any day, and reprint a receipt for any past cash or mobile money sale.

**7. Credit Book**
This is one of the most important pages for Kibuuka. Every credit sale is recorded against a specific customer with a repayment date. Customers can pay in installments and every payment is recorded. Overdue debts are highlighted in red. The Reports page shows the total outstanding credit every week so Kibuuka is never caught off-guard.

**8. Customers**
Every customer has a profile. Their full purchase history, credit history, and **Ka Money balance** are all visible in one place. This turns walk-in strangers into known, loyal customers.

**9. Ka Money Savings Jar**
This is the special feature from the case study. Every time a customer pays by Mobile Money, they earn 500 UGX in virtual savings. After 10 Mobile Money purchases, their balance becomes redeemable as a discount or reward. The receipt even shows "Ka Money Earned!" when it applies. This is a **loyalty programme** that costs Kibuuka almost nothing but gives customers a strong reason to keep coming back — and specifically to use Mobile Money, which is traceable and reliable.

**10. Staff Management**
Shop assistants are registered with their name, age, contact, start date, shift, and daily wage (8,000 UGX/day as specified in the case study). The owner can see who is active, which shift they work, and edit their details. Assistants log in with limited permissions — they record sales but cannot modify credit or delete products.

**11. Reports**
Every week the system automatically generates: Top 10 selling products, Revenue vs Cost of Goods (so you see actual profit), Outstanding credit total, Overdue credit list, Low stock alerts, and a breakdown of sales by payment method. No calculations needed — it's all automatic.

**12. Receipt**
A clean, branded, printable receipt is generated for every cash and mobile money sale. It has the shop name, location, receipt number, product, quantity, total, payment method confirmation, and a Ka Money notice where applicable. Credit customers get nothing — because credit hasn't been paid yet, there is nothing to confirm.

---

## 🎤 my Demo Pitch to the Panel


*"The problem Kibuuka faces is the same problem facing thousands of small shops across Kampala. Stock goes missing because nobody is tracking it properly. Customers buy on credit and 'forget' to pay. The owner has no idea which products are actually making money. And at the end of the week, there's no way to know if the shop made a profit or a loss.*

*My solution digitizes the entire operation. Let me show you.*

*When the owner logs in, the Dashboard tells them everything important before they've even had their morning tea — today's revenue, low stock alerts, and how much credit is outstanding.*

*When a sale happens, the assistant records it here in Record Sale. The system automatically reduces the stock — no manual counting. If the customer pays by Cash or Mobile Money, a receipt prints immediately. If it's credit — no receipt. The customer gets a receipt when they pay.*

*The Credit Book is where Kibuuka gets real power. Every customer who buys on credit is tracked here. When they come to pay, the assistant records the installment. The system updates the balance automatically. Overdue accounts are flagged in red so Kibuuka knows exactly who to follow up with.*

*Now the special feature — Ka Money. Every Mobile Money transaction earns the customer 500 UGX in virtual savings, shown right on their receipt. After 10 purchases, it becomes redeemable. This is a loyalty programme built into the shop system at zero extra cost. It also encourages customers to use Mobile Money, which means Kibuuka has a digital record of every transaction — much safer than cash.*

*And at the end of every week, the Reports page does all the accounting automatically. Top 10 products, profit vs expenses, overdue credit, low stock alerts — everything Kibuuka needs to make smart business decisions.*

*This runs on any browser, including low-end Android phones. No expensive hardware. No complicated setup. One server in the shop, staff connect on their phones over Wi-Fi."*

## ⭐ What Makes my Project Stand Out

**1. Role-based access that mirrors real shop operations.** Assistants can sell but cannot manipulate credit or delete stock. This prevents internal theft and unauthorized changes — a real problem in small shops.

**2. The receipt system is tied to payment reality.** Credit buyers don't get receipts. Cash and Mobile Money buyers get one instantly. No other student project likely has this level of business logic baked in.

**3. Ka Money is fully implemented, not just mentioned.** The loyalty system actually tracks balances, counts mobile purchases, shows on receipts, and has a redemption flow with a confirmation screen. Most students will write it in their wireframes. Yours actually works.

**4. Every action has a paper trail.** Restock history tracks suppliers and prices over time. Every sale records who made it. Every credit payment records who received it. This is audit-ready.

**5. It's designed for the actual user.** Large buttons, clean layouts, works on a small Android screen, and the language is simple. A shop assistant with basic phone literacy can use this after 10 minutes of training.
Ka Money Balance
This starts at 0 for every new customer. Every time that customer pays for something using Mobile Money, the system automatically adds 500 UGX to this field. You never touch it manually. It grows on its own as the customer keeps buying with Mobile Money.

Mobile Money Purchases
This also starts at 0. Every time that customer pays using Mobile Money, the system automatically counts it and adds 1 here. So if a customer has bought 7 times using Mobile Money, this field shows 7. Again, you never fill this yourself.

When Do They Matter?
When Mobile Money Purchases reaches 10, the system marks that customer as eligible to redeem their Ka Money savings. At that point on the Customer Detail page, a "Redeem Now" button appears in the Ka Money card. You click it, the customer gets their saved UGX as a reward, and both fields reset back to 0 to start the cycle again.