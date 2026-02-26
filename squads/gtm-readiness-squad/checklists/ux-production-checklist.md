# UX Production Readiness Checklist

Use this checklist for UX audit track validation.

## Core Search Flow

- [ ] Landing → Login → Search navigable
- [ ] UF selector: single, multi, "Todo o Brasil"
- [ ] Date range: default 10 days, custom works
- [ ] Sector selector: all 15 sectors displayed
- [ ] Submit: triggers search with progress
- [ ] Results: displayed in readable format
- [ ] Download: Excel generates and downloads
- [ ] Empty: helpful message with suggestions

## Progress & Feedback

- [ ] Progress bar starts within 2s of submit
- [ ] Progress advances smoothly (no long freezes)
- [ ] Per-UF status visible during search
- [ ] Source badges show which APIs responded
- [ ] Estimated time reasonable
- [ ] Completion celebration/transition smooth

## Error Handling

- [ ] Single error message per error (no doubles)
- [ ] Network error: clear, actionable message
- [ ] Timeout: suggests fewer UFs
- [ ] Partial results: shown with explanation
- [ ] Auth expired: redirect to login
- [ ] Server error: apologetic, suggests retry
- [ ] All errors in Portuguese

## Onboarding

- [ ] New user redirected to onboarding
- [ ] Each step has clear instructions
- [ ] CNAE: helper text or optional
- [ ] Skip/later option available
- [ ] Completion → first search guided

## Navigation & Layout

- [ ] Header: logo, nav links, user menu
- [ ] Footer: legal links, contact
- [ ] Breadcrumbs or clear location
- [ ] Mobile hamburger menu works
- [ ] All pages load under 3s
- [ ] No broken links (404s)

## Visual Consistency

- [ ] Color scheme consistent
- [ ] Typography hierarchy clear
- [ ] Spacing and padding consistent
- [ ] Icons render correctly
- [ ] Emojis display cross-platform
- [ ] Dark/light theme works (if applicable)

## Accessibility

- [ ] Semantic HTML (headings, landmarks)
- [ ] Alt text on images
- [ ] Focus visible on interactive elements
- [ ] Color contrast meets WCAG AA
- [ ] Keyboard navigation functional
- [ ] Screen reader compatible (basic)

## Mobile Specific

- [ ] Touch targets >= 44px
- [ ] No horizontal scroll
- [ ] Forms usable on small screens
- [ ] Modals don't overflow viewport
- [ ] Pinch-to-zoom not disabled

## Quick UX Check

For rapid validation:
- [ ] Can complete a search in under 2 minutes
- [ ] Can download results
- [ ] No confusing error messages
- [ ] Works on mobile phone
