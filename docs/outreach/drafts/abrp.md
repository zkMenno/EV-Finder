---
status: draft
to: ABRP / Iternio, contact page (abetterrouteplanner.com/contact) or support (abrp.featurebase.app); no email address is published
language: English
subject: Deep linking to ABRP with the car model pre-selected from [site name]
---

Hi,

I'm Menno, a Dutch freelancer based in France. I'm building [site name], a free and independent finder for used electric cars in Europe and the UK. It has no ads, no paid rankings and no hosted listings.

We don't plan trips ourselves. On each model page we'd like a "Plan a trip with this car in ABRP" link that opens ABRP with the car already chosen, using the `typecode` parameter from your deep-link documentation. Plain links with a UTM tag, opening in a new tab, no ABRP logo unless you allow it.

Two questions:

1. Is it fine to deep link to ABRP like this from public model pages?
2. Where can I find the current list of typecode values, and how will you announce changes to it?

If you'd prefer a different integration, I'll follow your guidance.

Thanks,
Menno
[reply-to email] · [site name]

## Notes for Menno

- Contact route: ABRP's API page links a contact page and a support portal, and shows no email. Use abetterrouteplanner.com/contact.
- The parameter name and accepted values live in their Deep Links documentation, not on the API page I read. Confirm the exact name (`typecode` is your spec's term) before sending, and edit the email if it differs.
- This closes the open item in the charging-buildout spec: until they answer, ship the plain ABRP link.
- Follow up after 2 weeks.
