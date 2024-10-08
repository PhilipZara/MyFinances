from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_POST

from backend.decorators import web_require_scopes, htmx_only
from backend.models import InvoiceRecurringProfile, Invoice
from backend.service.defaults.get import get_account_defaults
from backend.service.invoices.recurring.generation.next_invoice import generate_next_invoice_service
from backend.types.requests import WebRequest

import logging

logger = logging.getLogger(__name__)


@require_POST
@htmx_only("invoices:recurring:dashboard")
@web_require_scopes("invoices:write", True, True)
def generate_next_invoice_now_endpoint(request: WebRequest, invoice_profile_id):
    context: dict = {}
    invoice_recurring_profile: InvoiceRecurringProfile | None = InvoiceRecurringProfile.objects.filter(
        pk=invoice_profile_id, active=True
    ).first()

    if not invoice_recurring_profile:
        messages.error(request, "Failed to fetch next invoice; cannot find Invoice recurring profile.")
        return render(request, "base/toast.html")

    if invoice_recurring_profile.client_to:
        account_defaults = get_account_defaults(invoice_recurring_profile.owner, invoice_recurring_profile.client_to)
    else:
        account_defaults = get_account_defaults(invoice_recurring_profile.owner)

    if not invoice_recurring_profile.has_access(request.user):
        messages.error(request, "You do not have permission to modify this invoice recurring profile.")
        return render(request, "base/toast.html")

    next_invoice_issue_date = invoice_recurring_profile.next_invoice_issue_date()

    svc_resp = generate_next_invoice_service(
        invoice_recurring_profile=invoice_recurring_profile, issue_date=next_invoice_issue_date, account_defaults=account_defaults
    )

    if svc_resp.success:
        context["next_invoice_issue_date"] = invoice_recurring_profile.next_invoice_issue_date()
        context["next_invoice_due_date"] = invoice_recurring_profile.next_invoice_due_date(
            account_defaults=account_defaults, from_date=context["next_invoice_issue_date"]
        )

        return render(
            request, "pages/invoices/recurring/manage/next_invoice_block.html", {"invoiceProfile": invoice_recurring_profile} | context
        )
    else:
        logger.info(svc_resp.error)
        messages.error(request, "Failed to fetch next invoice; cannot find invoice recurring profile.")
        return render(request, "base/toast.html")
