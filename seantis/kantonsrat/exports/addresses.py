import tablib

from five import grok
from seantis.kantonsrat import _
from seantis.people.interfaces import IExportVariant, IList


class KantonsratAddressVariants(object):

    @property
    def adjusted_fields(self):
        raise NotImplementedError

    @property
    def multiline_fields(self):
        raise NotImplementedError

    def can_handle_type(self, fti):
        return fti.id == 'seantis.kantonsrat.member'

    def split_multiline_cell(self, cell_value):
        return [l for l in (v.strip() for v in cell_value.split('\n')) if l]

    def adjust_dataset(self, dataset, parameters):
        fields = parameters['export_fields']

        # make sure all required fields were selected
        for field in self.adjusted_fields:
            if field not in fields:
                return None

        header_map = dict(zip(fields, dataset.headers))
        column_map = dict(zip(fields, range(0, len(fields))))

        # sort the dataset by lastname -> firstname
        dataset = dataset.sort(column_map['firstname'])
        dataset = dataset.sort(column_map['lastname'])

        # get the number of columns for cells that are expanded into
        # multiple columns if they have multiple lines
        multiline_header_widths = {}

        for field in self.multiline_fields:
            for value in dataset[header_map[field]]:
                multiline_header_widths[field] = max(
                    multiline_header_widths.get(field, 0), len(
                        self.split_multiline_cell(value)
                    )
                )

        # build the new headers
        adjusted_headers = []
        for field in self.adjusted_fields:

            # include the extra headers generated by multiline cells
            if field in multiline_header_widths:
                for i in range(1, multiline_header_widths[field] + 1):
                    adjusted_headers.append(header_map[field] + " " + str(i))
            else:
                adjusted_headers.append(header_map[field])

        adjusted_dataset = tablib.Dataset(headers=adjusted_headers)

        # build the new row
        for row in dataset:
            new_row = []

            for field in self.adjusted_fields:
                value = row[column_map[field]]

                # expand some cells into multiline cells
                if field in multiline_header_widths:
                    values = [""] * multiline_header_widths[field]

                    for i, v in enumerate(self.split_multiline_cell(value)):
                        values[i] = v

                    new_row.extend(values)
                else:
                    new_row.append(value)

            adjusted_dataset.append(new_row)

        return adjusted_dataset


class KantonsratAddressLabelsVariant(grok.Adapter, KantonsratAddressVariants):

    grok.name('kantonsrat-address-labels')
    grok.provides(IExportVariant)
    grok.context(IList)

    title = _(u"Kantonsrat Address Labels")

    adjusted_fields = (
        'address_salutation',
        'firstname',
        'lastname',
        'address',
    )

    multiline_fields = (
        'address',
    )


class KantonsratAddressesVariant(grok.Adapter, KantonsratAddressVariants):

    grok.name('kantonsrat-addresses-variant')
    grok.provides(IExportVariant)
    grok.context(IList)

    title = _(u"Kantonsrat Addresses")

    adjusted_fields = (
        'salutation',
        'address_salutation',
        'letter_salutation',
        'lastname',
        'firstname',
        'function',
        'address',
        'document_dispatch_address',
        'phone',
        'mobile',
        'email',
        'secondary_email',
        'website',
        'fax',
        'bussiness_phone',  # XXX fix typo in kantonsrat.xml
        'business_fax',
        'birthday',
        'place_of_citizenship',
        'profession',
        'academic_title',
        'party_memberships',
        'faction_memberships',
        'electoral_district',
        'private_address',
        'entry_date',
        'start',
        'end'
    )

    multiline_fields = (
        'address',
        'document_dispatch_address',
        'private_address'
    )