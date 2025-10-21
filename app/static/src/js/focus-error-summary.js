import { setFocus } from "govuk-frontend/dist/govuk/common/index.mjs";

const anchorLocation = window.location.hash;

if (anchorLocation) {
  setTimeout(() => {
    const errorSummaryElements = document.getElementsByClassName(
      "govuk-error-summary"
    );
    if (errorSummaryElements.length > 0) {
      setFocus(errorSummaryElements[0]);
    }
  }, 10);
}