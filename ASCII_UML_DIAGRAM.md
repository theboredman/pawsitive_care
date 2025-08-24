# ASCII UML Class Diagram - Pawsitive Care

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PAWSITIVE CARE - UML CLASS DIAGRAM                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    ACCOUNTS     │    │       PETS       │    │  APPOINTMENTS   │    │     BILLING     │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤    ├─────────────────┤
│  CustomUser     │    │  Pet             │    │  AppointmentType│    │  ServiceCost    │
│  ┌─────────────┐│    │  ┌──────────────┐│    │  ┌─────────────┐│    │  ┌─────────────┐│
│  │ -username   ││    │  │ -name        ││    │  │ -name       ││    │  │ -service_   ││
│  │ -email      ││    │  │ -species     ││    │  │ -description││    │  │  type       ││
│  │ -phone      ││    │  │ -breed       ││    │  │ -base_cost  ││    │  │ -cost       ││
│  │ -address    ││    │  │ -age         ││    │  └─────────────┘│    │  └─────────────┘│
│  │ -role       ││    │  │ -gender      ││    │                 │    │                 │
│  └─────────────┘│    │  │ -weight      ││    │  Appointment    │    │  Billing        │
│                 │    │  │ -owner_id    ││    │  ┌─────────────┐│    │  ┌─────────────┐│
│                 │    │  └──────────────┘│    │  │ -pet_id     ││    │  │ -appoint_id ││
│                 │    │                  │    │  │ -vet_id     ││    │  │ -pet_id     ││
│                 │    │  MedicalRecord   │    │  │ -client_id  ││    │  │ -owner_id   ││
│                 │    │  ┌──────────────┐│    │  │ -date       ││    │  │ -service_id ││
│                 │    │  │ -pet_id      ││    │  │ -time       ││    │  │ -amount     ││
│                 │    │  │ -date        ││    │  │ -status     ││    │  │ -status     ││
│                 │    │  │ -record_type ││    │  └─────────────┘│    │  └─────────────┘│
│                 │    │  │ -description ││    │                 │    │                 │
│                 │    │  └──────────────┘│    │                 │    │                 │
│                 │    │                  │    │                 │    │                 │
│                 │    │  PetPhoto        │    │                 │    │                 │
│                 │    │  ┌──────────────┐│    │                 │    │                 │
│                 │    │  │ -pet_id      ││    │                 │    │                 │
│                 │    │  │ -image       ││    │                 │    │                 │
│                 │    │  │ -is_primary  ││    │                 │    │                 │
│                 │    │  └──────────────┘│    │                 │    │                 │
│                 │    │                  │    │                 │    │                 │
│                 │    │  PetDocument     │    │                 │    │                 │
│                 │    │  ┌──────────────┐│    │                 │    │                 │
│                 │    │  │ -pet_id      ││    │                 │    │                 │
│                 │    │  │ -file        ││    │                 │    │                 │
│                 │    │  │ -doc_type    ││    │                 │    │                 │
│                 │    │  └──────────────┘│    │                 │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  INVENTORY                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  InventoryItem              StockMovement             Supplier                      │
│  ┌─────────────────┐        ┌─────────────────┐      ┌─────────────────┐           │
│  │ -name           │        │ -item_id        │      │ -name           │           │
│  │ -sku            │        │ -movement_type  │      │ -contact_person │           │
│  │ -category       │        │ -quantity       │      │ -email          │           │
│  │ -unit_price     │        │ -reason         │      │ -phone          │           │
│  │ -quantity       │        │ -old_quantity   │      │ -address        │           │
│  │ -supplier_id    │        │ -new_quantity   │      └─────────────────┘           │
│  └─────────────────┘        └─────────────────┘                                    │
│                                                                                     │
│  PurchaseOrder              PurchaseOrderItem                                      │
│  ┌─────────────────┐        ┌─────────────────┐                                   │
│  │ -order_number   │        │ -purchase_ord_id│                                   │
│  │ -supplier_id    │        │ -item_id        │                                   │
│  │ -status         │        │ -quantity_ord   │                                   │
│  │ -order_date     │        │ -quantity_recv  │                                   │
│  │ -total_amount   │        │ -unit_price     │                                   │
│  └─────────────────┘        └─────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  PETMEDIA                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  BlogCategory               BlogPost                  BlogComment                   │
│  ┌─────────────────┐        ┌─────────────────┐      ┌─────────────────┐           │
│  │ -name           │        │ -title          │      │ -post_id        │           │
│  │ -description    │        │ -content        │      │ -author_id      │           │
│  │ -icon           │        │ -author_id      │      │ -content        │           │
│  │ -is_active      │        │ -category_id    │      │ -parent_id      │           │
│  └─────────────────┘        │ -related_pet_id │      │ -is_approved    │           │
│                             │ -is_published   │      └─────────────────┘           │
│  BlogLike                   │ -slug           │                                    │
│  ┌─────────────────┐        │ -views_count    │                                    │
│  │ -post_id        │        └─────────────────┘                                    │
│  │ -user_id        │                                                               │
│  └─────────────────┘                                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  RECORDS                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  PetsMedicalRecord                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐          │
│  │ -record_id (PK)                                                     │          │
│  │ -pet_id                                                             │          │
│  │ -vaterian_id                                                        │          │
│  │ -visit_date                                                         │          │
│  │ -treatment                                                          │          │
│  │ -prescription                                                       │          │
│  │ -vaccination_date                                                   │          │
│  │ -diagnosis                                                          │          │
│  │ -notes                                                              │          │
│  └─────────────────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────────┘

RELATIONSHIPS (Key Foreign Keys):
═══════════════════════════════════════
• CustomUser (1) ──── (M) Pet.owner_id
• CustomUser (1) ──── (M) Appointment.vet_id  
• CustomUser (1) ──── (M) Appointment.client_id
• Pet (1) ──── (M) MedicalRecord.pet_id
• Pet (1) ──── (M) PetPhoto.pet_id
• Pet (1) ──── (M) PetDocument.pet_id
• Pet (1) ──── (M) Appointment.pet_id
• Appointment (1) ──── (1) Billing.appointment_id
• ServiceCost (1) ──── (M) Billing.service_id
• InventoryItem (1) ──── (M) StockMovement.item_id
• Supplier (1) ──── (M) InventoryItem.supplier_id
• Supplier (1) ──── (M) PurchaseOrder.supplier_id
• PurchaseOrder (1) ──── (M) PurchaseOrderItem.purchase_order_id
• InventoryItem (1) ──── (M) PurchaseOrderItem.item_id
• BlogCategory (1) ──── (M) BlogPost.category_id
• BlogPost (1) ──── (M) BlogComment.post_id
• BlogPost (1) ──── (M) BlogLike.post_id
• CustomUser (1) ──── (M) BlogPost.author_id
• CustomUser (1) ──── (M) BlogComment.author_id
• Pet (1) ──── (M) PetsMedicalRecord.pet_id
• CustomUser (1) ──── (M) PetsMedicalRecord.vaterian_id

TOTAL: 19 Domain Model Classes
```
