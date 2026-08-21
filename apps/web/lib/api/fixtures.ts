/** Synthetic labeled fixtures uploaded through the API (not live registry data). */

export function buildInvoiceFixture(opts: {
  seller: string;
  lei?: string;
  quantity?: number;
  unit?: string;
  unitPrice?: number;
  invoiceNumber?: string;
}): string {
  const qty = opts.quantity ?? 500;
  const unit = opts.unit ?? "MT";
  const unitPrice = opts.unitPrice ?? 2500;
  const total = qty * unitPrice;
  return [
    `invoice_number: ${opts.invoiceNumber ?? "INV-TP-1001"}`,
    "invoice_date: 2026-03-01",
    "currency: USD",
    `seller: ${opts.seller}`,
    opts.lei ? `seller_lei: ${opts.lei}` : "seller_lei:",
    "buyer: Gulf Importers LLC",
    "description: Copper cathodes Grade A",
    `quantity: ${qty}`,
    `unit: ${unit}`,
    `unit_price: ${unitPrice}`,
    `line_total: ${total}`,
    `total_amount: ${total}`,
    "hs_code: 740311",
    "port_of_loading: Mundra, IN",
    "port_of_discharge: Jebel Ali, AE",
  ].join("\n");
}

export function buildBolFixture(opts: {
  shipper: string;
  quantity?: number;
  unit?: string;
  blNumber?: string;
  invoiceNumber?: string;
}): string {
  const qty = opts.quantity ?? 500;
  const unit = opts.unit ?? "MT";
  return [
    `bl_number: ${opts.blNumber ?? "BL-TP-9001"}`,
    `shipper: ${opts.shipper}`,
    "consignee: Gulf Importers LLC",
    "goods_description: Copper cathodes Grade A",
    `quantity: ${qty}`,
    `unit: ${unit}`,
    "port_of_loading: Mundra, IN",
    "port_of_discharge: Jebel Ali, AE",
    `invoice_reference: ${opts.invoiceNumber ?? "INV-TP-1001"}`,
    "hs_code: 740311",
  ].join("\n");
}

/** Known GLEIF fixture LEI from API tests / fixture adapter. */
export const FIXTURE_LEI = "5493001KJTIIGC8Y1R12";
export const FIXTURE_SELLER = "Amit Trading Co.";
