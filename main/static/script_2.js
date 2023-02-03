myOptions = [
    { label: 'Options 1', value: '1', alias: 'custom label for search', classNames: 'customClassNames', },
    { label: 'Options 2', value: '2', description: 'custom description for label', customData: '' },
    { label: 'Options 3', value: '3' }
  ]

  VirtualSelect.init({
    ele: '#example-select',
    options: myOptions
  });