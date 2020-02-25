# -*- encoding: utf-8 -*-

# yapf: disable
# type: ignore



checkname = 'aws_glacier'


info = [[u'[{"SizeInBytes":',
         u'0,',
         u'"VaultARN":',
         u'"arn:aws:glacier:eu-central-1:710145618630:vaults/axi_empty_vault",',
         u'"VaultName":',
         u'"axi_empty_vault",',
         u'"Label":',
         u'"axi_empty_vault",',
         u'"Values":',
         u'[],',
         u'"NumberOfArchives":',
         u'0,',
         u'"Timestamps":',
         u'[],',
         u'"CreationDate":',
         u'"2019-07-22T09:39:34.135Z",',
         u'"Id":',
         u'"id_0_GlacierMetric",',
         u'"Tagging":',
         u'{},',
         u'"StatusCode":',
         u'"Complete"},',
        u'{"SizeInBytes":',
         u'22548578304,',
         u'"VaultARN":',
         u'"arn:aws:glacier:eu-central-1:710145618630:vaults/fake_vault_1",',
         u'"VaultName":',
         u'"fake_vault_1",',
         u'"Label":',
         u'"fake_vault_1",',
         u'"Values":',
         u'[],',
         u'"NumberOfArchives":',
         u'2025,',
         u'"Timestamps":',
         u'[],',
         u'"CreationDate":',
         u'"2019-07-18T08:07:01.708Z",',
         u'"Id":',
         u'"id_2_GlacierMetric",',
         u'"Tagging":',
         u'{},',
         u'"StatusCode":',
         u'"Complete"},',
         u'{"SizeInBytes":',
         u'117440512,',
         u'"VaultARN":',
         u'"arn:aws:glacier:eu-central-1:710145618630:vaults/fake_vault_2",',
         u'"VaultName":',
         u'"fake_vault_2",',
         u'"Label":',
         u'"fake_vault_2",',
         u'"Values":',
         u'[],',
         u'"NumberOfArchives":',
         u'17,',
         u'"Timestamps":',
         u'[],',
         u'"CreationDate":',
         u'"2019-07-18T08:07:01.708Z",',
         u'"Id":',
         u'"id_3_GlacierMetric",',
         u'"Tagging":',
         u'{},',
         u'"StatusCode":',
         u'"Complete"},',
         u'{"SizeInBytes":',
         u'0,',
         u'"VaultARN":',
         u'"arn:aws:glacier:eu-central-1:710145618630:vaults/axi_vault",',
         u'"VaultName":',
         u'"axi_vault",',
         u'"Label":',
         u'"axi_vault",',
         u'"Values":',
         u'[],',
         u'"NumberOfArchives":',
         u'0,',
         u'"Timestamps":',
         u'[],',
         u'"CreationDate":',
         u'"2019-07-18T08:07:01.708Z",',
         u'"Id":',
         u'"id_1_GlacierMetric",',
         u'"Tagging":',
         u'{},',
         u'"StatusCode":',
         u'"Complete"}]']]


discovery = {'': [(u'axi_empty_vault', {}), (u'axi_vault', {}), (u'fake_vault_1', {}), (u'fake_vault_2', {})], 'summary': [(None, {})]}


checks = {'': [
                (u'axi_empty_vault',
                {},
                [(0,
                  'Vault size: 0.00 B',
                  [('aws_glacier_vault_size', 0, None, None, None, None)]),
                 (0,
                  'Number of archives: 0',
                  [('aws_glacier_num_archives', 0, None, None, None, None)])]),

               (u'axi_vault',
                {},
                [(0,
                  'Vault size: 0.00 B',
                  [('aws_glacier_vault_size', 0, None, None, None, None)]),
                 (0,
                  'Number of archives: 0',
                  [('aws_glacier_num_archives', 0, None, None, None, None)])]),
                (u'fake_vault_1',
                {},
                [(0,
                  'Vault size: 21.00 GB',
                  [('aws_glacier_vault_size', 22548578304, None, None, None, None)]),
                 (0,
                  'Number of archives: 2025',
                  [('aws_glacier_num_archives', 2025, None, None, None, None)])]),
                (u'fake_vault_2',
                {},
                [(0,
                  'Vault size: 112.00 MB',
                  [('aws_glacier_vault_size', 117440512, None, None, None, None)]),
                 (0,
                  'Number of archives: 17',
                  [('aws_glacier_num_archives', 17, None, None, None, None)])])],
          'summary': [(None,
                       {},
                       [(0,
                         'Total size: 21.11 GB',
                         [('aws_glacier_total_vault_size',
                           22666018816,
                           None,
                           None,
                           None,
                           None)]),
                        (0,
                         u'Largest vault: fake_vault_1 (21.00 GB)',
                         [('aws_glacier_largest_vault_size',
                           22548578304,
                           None,
                           None,
                           None,
                           None)])])]}