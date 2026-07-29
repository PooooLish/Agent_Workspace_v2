---
name: visual-design-review
description: Use when designing, implementing, or reviewing a web page, app screen, dashboard, game UI, landing page, portfolio, or visual tool for hierarchy, layout, typography, color, accessibility, states, responsiveness, and visual polish.
---

# Visual Design Review

## Purpose

Improve an agent's judgment when designing or reviewing visual user interfaces. Use this skill to make frontend work more intentional, visually coherent, accessible, and aligned with the product's actual use case.

## When to use

Use when a task involves:

- building or revising a web page, app screen, dashboard, game UI, landing page, portfolio, or visual tool
- reviewing UI aesthetics, layout, typography, color, spacing, hierarchy, or interaction polish
- turning a functional prototype into a more credible product experience
- checking whether a design feels generic, cluttered, visually inconsistent, or hard to scan

Do not use this skill as a substitute for user research, brand strategy, or accessibility testing. It is a structured design review aid, not proof that a design is objectively good.

## Core principles

1. Fit the product type before choosing a style.
   - Operational tools should prioritize density, scanability, predictable controls, and low visual noise.
   - Consumer, portfolio, game, editorial, and brand pages can use more expressive composition, imagery, motion, and atmosphere.
   - Avoid applying a generic SaaS, gradient, or card-heavy style when the domain calls for something else.

2. Make hierarchy explicit.
   - Establish one clear primary action or primary reading path per view.
   - Use size, weight, spacing, alignment, and contrast to show importance.
   - Do not rely on color alone to communicate state or priority.

3. Keep visual design focused on essentials.
   - Remove decorative elements that compete with core content or actions.
   - Prefer fewer, stronger layout decisions over many weak embellishments.
   - Treat empty space as structure, not filler.

4. Preserve consistency and platform expectations.
   - Reuse existing tokens, components, spacing scales, icon styles, and interaction patterns.
   - Match the surrounding codebase before inventing a new design language.
   - Use familiar controls for familiar jobs: tabs for views, toggles for binary options, sliders or steppers for numeric values, menus for option sets.

5. Design for real content and real states.
   - Test long labels, empty states, loading states, errors, disabled states, narrow screens, and dense data.
   - Ensure text does not overflow, overlap, or hide controls.
   - Avoid layouts that only work with ideal placeholder copy.

6. Treat accessibility as part of aesthetics.
   - Maintain readable contrast, visible focus states, meaningful labels, keyboard reachability, and sufficient target size.
   - Use semantic structure where available.
   - A polished interface that excludes users is not a successful design.

7. Verify visually, not only by reading code.
   - When possible, run the UI and inspect screenshots at desktop and mobile widths.
   - Check alignment, framing, blank states, scroll behavior, text overflow, and whether assets actually render.
   - For canvas or 3D work, verify that the canvas is nonblank and correctly framed.

## Procedure

1. Identify the surface and audience.
   - Name the product type, primary user, main task, and expected usage frequency.
   - Decide whether the interface should feel operational, editorial, playful, premium, technical, calm, or expressive.

2. Inspect existing design constraints.
   - Read existing components, styles, design tokens, layout utilities, and icons.
   - Note dominant colors, typography, spacing, border radii, shadows, and interaction conventions.

3. Review the interface across seven dimensions.
   - Purpose fit: does the visual style match the domain and user task?
   - Hierarchy: is the user's next action or reading path obvious?
   - Layout: are alignment, spacing, grouping, and density deliberate?
   - Typography: are font sizes, weights, line lengths, and labels readable?
   - Color and contrast: do colors support meaning, hierarchy, and accessibility?
   - Interaction states: are hover, focus, active, loading, empty, error, and disabled states handled?
   - Responsiveness: does the design hold up on narrow and wide viewports?

4. Improve in small passes.
   - First fix structure and hierarchy.
   - Then fix spacing, typography, and grouping.
   - Then fix color, imagery, and motion.
   - Then fix edge states and responsive behavior.

5. Verify with concrete evidence.
   - Run the relevant build, test, lint, or preview command.
   - Use screenshots or browser inspection when the UI is visual.
   - Report what was actually checked and what remains unchecked.

## Review checklist

- The first viewport communicates the product, object, or task clearly.
- The primary action is visible and visually dominant without being noisy.
- Controls use familiar UI patterns instead of decorative substitutes.
- Text fits in its containers at realistic content lengths.
- Components align to a consistent grid or spacing rhythm.
- Color palette has clear roles and is not dominated by one accidental hue.
- Contrast is sufficient for normal text, small text, disabled states, and focus indicators.
- Repeated items have stable dimensions and do not shift during hover or loading.
- Cards are used for actual repeated items or framed tools, not as default page-section wrappers.
- Empty, loading, error, success, and disabled states are intentionally designed.
- Mobile and desktop layouts are both usable.
- Visual assets are relevant, rendered, and not merely atmospheric filler.

## Expected output

For design review:

- prioritized findings with concrete UI evidence
- suggested fixes tied to hierarchy, layout, typography, color, states, or responsiveness
- verification notes and remaining risks

For implementation:

- minimal, scoped UI changes that fit the existing codebase
- updated styles/components only where needed
- verification command results and visual inspection summary

## References

- Nielsen Norman Group, "10 Usability Heuristics for User Interface Design": https://www.nngroup.com/articles/ten-usability-heuristics/
- W3C, "Web Content Accessibility Guidelines (WCAG) 2.2": https://www.w3.org/TR/WCAG22/
- Google Material Design 3: https://m3.material.io/
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
