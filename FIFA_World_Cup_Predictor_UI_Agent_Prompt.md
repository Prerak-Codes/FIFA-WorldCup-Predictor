# AI Agent Task: Improve FIFA World Cup Predictor UI

You are working on an existing **FIFA World Cup Predictor** web application. Analyze the current codebase first and then implement the following UI/UX improvements. Do not break any existing prediction logic, machine-learning functionality, data loading, calculations, or application features.

## Main Goal

Transform the current interface into a more modern, professional, polished, and visually consistent football analytics application.

## Required Changes

### 1. Remove unnecessary Streamlit branding/actions
- Remove the visible **Deploy** button/action from the application UI if it is being exposed through the app layout or custom UI.
- Remove text such as:
  - `Built with Streamlit`
  - `Powered by XGBoost`
  - `Data: FIFA/Elo ratings`
  - `Made with these technologies`
- Remove unnecessary technology badges or footer content that makes the UI look like a development/demo project.
- Keep the interface clean and production-focused.

### 2. Improve the overall theme
Create a premium, modern football analytics theme.

The design should feel like a professional sports analytics dashboard rather than a basic Streamlit application.

Use:
- A clean dark theme
- Strong visual hierarchy
- Modern typography
- Consistent spacing and alignment
- Subtle borders and shadows
- Rounded cards and controls
- A professional accent color system inspired by football/sports analytics
- Good contrast and readability

Avoid excessive colors, excessive gradients, clutter, or overly decorative elements.

### 3. Improve the sidebar
Redesign the sidebar to look cleaner and more professional.

Include:
- Application name/logo area
- Useful model information presented cleanly
- Better spacing and typography
- Important statistics displayed as compact cards or metrics where appropriate

Do not show unnecessary technical/development information.

### 4. Improve the navigation tabs
The current sections include:
- Head-to-Head Predictor
- World Cup Bracket Simulator
- Team Analytics Explorer

Improve the visual design so they:
- Look consistent with the overall theme
- Clearly show the active section
- Have good spacing
- Are easy to understand
- Work properly on different screen sizes

Do not remove any existing functionality.

### 5. Improve the Head-to-Head Predictor page
Redesign the main predictor section.

Improve:
- Home team selector
- Away team selector
- VS presentation
- Neutral venue control
- Tournament selector
- Year input
- Prediction result area

The team selection area should feel balanced and visually organized.

Make the **VS** element visually attractive without making it too large.

### 6. Improve the prediction result section
Make the prediction output the main visual focus after the user selects teams.

Clearly display:
- Predicted result
- Home win probability
- Draw probability
- Away win probability

Use professional cards, metrics, progress bars, or charts where appropriate.

The probabilities should be easy to understand immediately.

Use clear labels:
- Home Win
- Draw
- Away Win

Make sure colors are consistent and accessible.

### 7. Improve responsiveness
Ensure the UI works properly on:
- Desktop
- Laptop
- Smaller screens

Avoid broken layouts, excessive horizontal scrolling, overlapping components, or poorly aligned controls.

### 8. Improve consistency
Apply the same design system throughout the entire application:
- Consistent colors
- Consistent typography
- Consistent border radius
- Consistent spacing
- Consistent button styles
- Consistent cards and containers

### 9. Keep functionality intact
This is very important:

- Do NOT remove prediction functionality.
- Do NOT modify or break the XGBoost model.
- Do NOT break the World Cup Bracket Simulator.
- Do NOT break the Team Analytics Explorer.
- Do NOT change the machine-learning pipeline unless absolutely necessary.
- Focus primarily on UI, UX, layout, styling, and presentation.

### 10. Clean up the code
While implementing the new UI:
- Remove unused UI code
- Remove unnecessary styling
- Organize reusable UI components where appropriate
- Keep the code readable and maintainable
- Avoid duplicate styling logic

## Expected Final Result

The final application should look like a polished, production-quality **FIFA World Cup football analytics platform**.

It should feel:
- Modern
- Professional
- Clean
- Premium
- Easy to use
- Visually consistent

The application should no longer look like a default Streamlit project or a student/demo interface.

Before finishing, test all major sections and confirm that:
1. Head-to-Head Predictor works correctly.
2. World Cup Bracket Simulator works correctly.
3. Team Analytics Explorer works correctly.
4. Prediction probabilities display correctly.
5. No existing ML functionality is broken.
6. The updated UI is visually consistent across the application.

Implement these improvements directly in the existing project structure and preserve all working functionality.
