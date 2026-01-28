export interface ComplaintField {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'date' | 'time';
  required?: boolean;
  options?: string[];
  showFor?: ('customer' | 'staff')[];
}

export const ComplaintFieldConfig: ComplaintField[] = [
  {
    key: 'date_of_issue',
    label: 'Date of Issue',
    type: 'date',
    required: true,
    showFor: ['customer', 'staff']
  },
  {
    key: 'reporting_time',
    label: 'Reporting Time',
    type: 'time',
    required: true,
    showFor: ['customer', 'staff']
  },
  {
    key: 'reporting_mode',
    label: 'Reporting Mode',
    type: 'select',
    required: true,
    options: ['mail', 'call', 'message', 'app'],
    showFor: ['customer', 'staff']
  },
  {
    key: 'problem_type',
    label: 'Problem Type',
    type: 'select',
    required: true,
    options: ['smart_card', 'smart_pass', 'tickets', 'bus_service', 'staff', 'others'],
    showFor: ['customer', 'staff']
  },
  {
    key: 'sub_problem_type',
    label: 'Sub Problem Type',
    type: 'select',
    required: true,
    options: [
      'website_recharge', 'mobile_app_recharge', 'etim_val_recharge',
      'smartcity_card_recharge', 'smart_pass_application',
      'smart_pass_renewal', 'smart_card_application', 'lost_card',
      'lost_pass', 'refund'
    ],
    showFor: ['customer', 'staff']
  },
  {
    key: 'reference_type',
    label: 'Reference Type',
    type: 'select',
    required: false,
    options: ['app_no', 'card_no', 'email', 'utr', 'mobile'],
    showFor: ['staff']
  },
  {
    key: 'reference_no',
    label: 'Reference Number',
    type: 'text',
    required: false,
    showFor: ['staff']
  },
  {
    key: 'problem_description',
    label: 'Problem Description',
    type: 'textarea',
    required: true,
    showFor: ['customer', 'staff']
  }
];
