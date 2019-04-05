class Record(dict):
    """A dictionary holding information from a Medline record. 

    All data are stored under the mnemonic appearing in the Medline
    file. These mnemonics have the following interpretations:

    ========= ==============================
    Mnemonic  Description
    --------- ------------------------------
    AB        Abstract
    CI        Copyright Information
    AD        Affiliation
    IRAD      Investigator Affiliation
    AID       Article Identifier
    AU        Author
    FAU       Full Author
    CN        Corporate Author
    DCOM      Date Completed
    DA        Date Created
    LR        Date Last Revised
    DEP       Date of Electronic Publication
    DP        Date of Publication
    EDAT      Entrez Date
    GS        Gene Symbol
    GN        General Note
    GR        Grant Number
    IR        Investigator Name
    FIR       Full Investigator Name
    IS        ISSN
    IP        Issue
    TA        Journal Title Abbreviation
    JT        Journal Title
    LA        Language
    LID       Location Identifier
    MID       Manuscript Identifier
    MHDA      MeSH Date
    MH        MeSH Terms
    JID       NLM Unique ID
    RF        Number of References
    OAB       Other Abstract
    OCI       Other Copyright Information
    OID       Other ID
    OT        Other Term
    OTO       Other Term Owner
    OWN       Owner
    PG        Pagination
    PS        Personal Name as Subject
    FPS       Full Personal Name as Subject
    PL        Place of Publication
    PHST      Publication History Status
    PST       Publication Status
    PT        Publication Type
    PUBM      Publishing Model
    PMC       PubMed Central Identifier
    PMID      PubMed Unique Identifier
    RN        Registry Number/EC Number
    NM        Substance Name
    SI        Secondary Source ID
    SO        Source
    SFM       Space Flight Mission
    STAT      Status
    SB        Subset
    TI        Title
    TT        Transliterated Title
    VI        Volume
    CON       Comment on
    CIN       Comment in
    EIN       Erratum in
    EFR       Erratum for
    CRI       Corrected and Republished in
    CRF       Corrected and Republished from
    PRIN      Partial retraction in
    PROF      Partial retraction of
    RPI       Republished in
    RPF       Republished from
    RIN       Retraction in
    ROF       Retraction of
    UIN       Update in
    UOF       Update of
    SPIN      Summary for patients in
    ORI       Original report in
    ========= ==============================

    """


def parse(handle):
    """
    Read Medline records one by one from the handle.

    :param handle: either is a Medline file, a file-like object, or a list of lines describing one or more Medline
    records
    :return: a generator with each of the records
    """

    # These keys point to string values
    textkeys = ("ID", "PMID", "SO", "RF", "NI", "OT", "JC", "TA", "IS", "CY", "TT",
                "CA", "IP", "VI", "DP", "YR", "PG", "LID", "DA", "LR", "OWN",
                "STAT", "DCOM", "PUBM", "DEP", "PL", "JID", "SB", "PMC",
                "EDAT", "MHDA", "PST", "AB", "AD", "EA", "TI", "JT")
    handle = iter(handle)

    key = ""
    record = Record()

    # flag use to make sure it is still going through the same author
    new_author = False

    # loop through all the lines in the file
    for line in handle:
        # returns a copy of the string in which all chars have been stripped from the end of the string
        line = line.rstrip()
        # need to account for information that occupies more than one line
        if line[:6] == "      ":  # continuation line
            if key == 'MH':
                # Multi-line MESH term, want to append to last entry in list
                record[key][-1] += line[5:]  # including space using line[5:]
            # the affiliations (AD) are put on list of list because there is a list created under the dictionary key
            # for every author
            elif key == 'AD':
                # Multi-line affiliation term, want to append to last entry in list
                record[key][-1][-1] += line[6:]
            # everything else is just added
            else:
                record[key].append(line[6:])
        # if it is a key-value pair
        elif line:
            # obtain the key
            key = line[:4].rstrip()
            # a new key that is not AD
            if key not in record and key != 'AD':
                record[key] = list()
                record[key].append(line[6:])
            # a known key that it is not AD
            elif key != 'AD':
                record[key].append(line[6:])
            # AD. The affiliation values has to be put in list of list because there are multiple affiliations per
            # author and if we just add affiliations to the same list, we loose to which author that affiliation(s)
            # belongs to
            else:
                # if key is already added just obtain the list of list
                if key in record.keys():
                    tmp = record[key]
                # or create a new one if he key has not been seen
                else:
                    tmp = list()
                # add the new value as a list to the tmp list i.e. adding another level
                if not new_author:
                    tmp[-1][-1] += ';' + line[6:] + ' '
                else:
                    tmp.append([line[6:]])
                # insert the new list to that key
                record[key] = tmp

                new_author = False

            if key == 'FAU':
                new_author = True

        # empty line
        elif record:
            # Join each list of strings into one string.
            for key in record:
                if key in textkeys:
                    if key == 'AD':
                        # Flatten the list of affiliations to "remove the brackets" using a nested list comprehension
                        record[key] = [element for sub_list in record[key] for element in sub_list]
                    elif key == 'OT' or key == 'MH':
                        record[key] = ';'.join(record[key])
                    else:
                        record[key] = " ".join(record[key])
            yield record
            record = Record()

    if record:  # catch last one
        for key in record:
            if key in textkeys:
                if key == 'AD':
                    # Flatten the list of affiliations to "remove the brackets" using a nested list comprehension
                    record[key] = [element for sub_list in record[key] for element in sub_list]
                elif key == 'OT' or key == 'MH':
                    record[key] = ';'.join(record[key])
                else:
                    record[key] = " ".join(record[key])
        yield record
