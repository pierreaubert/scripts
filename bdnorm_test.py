#!/usr/bin/python
# -*- coding: utf-8 -*-
# normalise names in comics directory
# convention is as follow
#    series/Series_01_Title.suf
# ----------------------------------------------------------------------

import unittest
import bdnorm

# ----------------------------------------------------------------------
# list of test
# first is the test field and then the 4 answers
# ----------------------------------------------------------------------
datas_base = [
    ['series_12_title.pdf',       'Series',  '12', 'Title', 'pdf'],
    ['series 12 title.pdf',       'Series',  '12', 'Title', 'pdf'],
    ['series-12-title.pdf',       'Series',  '12', 'Title', 'pdf'],
    ['series-T12-title.pdf',      'Series',  '12', 'Title', 'pdf'],
    ['series-tome12-title.pdf',   'Series',  '12', 'Title', 'pdf'],
    ['series-Tome12-title.pdf',   'Series',  '12', 'Title', 'pdf'],
    ['series-Tomes12-title.pdf',  'Series',  '12', 'Title', 'pdf'],
    ['series-Tome 12-title.pdf',  'Series',  '12', 'Title', 'pdf'],
    ['series-Tomes 12-title.pdf', 'Series',  '12', 'Title', 'pdf'],
    ['series-Tomes_12-title.pdf', 'Series',  '12', 'Title', 'pdf']
]
datas_without_series = [
    # without series
    ['12-title.pdf',              '',        '12', 'Title', 'pdf'],
    ['12 title.pdf',              '',        '12', 'Title', 'pdf'],
    ['12_title.pdf',              '',        '12', 'Title', 'pdf'],
    ['12 - title.pdf',            '',        '12', 'Title', 'pdf'],
    ['T12 _ title.pdf',           '',        '12', 'Title', 'pdf']
]
datas_real_life = [
    # real life
    ['XIII 01 - Le jour du soleil noir.cbr', 'XIII', '01', 'Le.Jour.du.Soleil.Noir', 'cbr'],
    # with char utf8
    ['XIII 02 - Là où va l Indien.cbr', 'XIII', '02', 'La.ou.Va.l.Indien', 'cbr'],
    # with name in title inside ()
    ['XIII 18 - La version Irlandaise (Van.Hamme-Vance).cbr', 'XIII', '18', 'La.Version.Irlandaise', 'cbr'],
    # with spaces inside series and title
    ['XIII Mystery - T01 - La Mangouste.pdf', 'XIII.Mystery', '01', 'La.Mangouste', 'pdf'],
    ['XIII Mystery - T04 - Colonel Amos.cbz', 'XIII.Mystery', '04', 'Colonel.Amos', 'cbz'],
    ['XIII Mystery T2 - Irina.zip',           'XIII.Mystery', '2', 'Irina', 'zip'],
    # with tome but without title
    ['Les Bidochon - tome 19 - Zoro.pdf',             'Les.Bidochon', '19', 'Zoro', 'pdf'],
    ['Les Bidochon - tome 19.pdf',             'Les.Bidochon', '19', '', 'pdf'],
    # more complicated, stupid case starting with a number
    ['4 Princes de Ganahan 1. Galin.pdf',     '4.Princes.de.Ganahan', '1', 'Galin', 'pdf'],
    # error without serie
    ["01_La.fugue.d'Aria.zip", '', '01', 'La.Fugue.d.Aria', 'zip'],
    # prb with unicode
    ['Assassin Royal - T01 - Le Bâtard.cbr', 'Assassin.Royal', '01', 'Le.Batard', 'cbr'],
    # strange error
    ['VenusH_01 - Anja.zip', 'Venush', '01', 'Anja', 'zip'],
    # dealing with HS
    ['Valerian HS - Par Les Chemins De L Espace.cbr', 'Valerian', 'HS', 'Par.les.Chemins.de.l.Espace', 'cbr'],
    ['Valerian THS - Par Les Chemins De L Espace.cbr', 'Valerian', 'HS', 'Par.les.Chemins.de.l.Espace', 'cbr'],
    # encoding prb
    ['Yoko.Tsuno_06_Les.3.Soleils.de.Vinéa.zip', 'Yoko.Tsuno', '06', 'Les.3.Soleils.de.Vinea', 'zip'],
    # complex with 2 numbers
    ['BD.FR.-.Waterloo.1911.-.T02.-.Welly.le.petit.(Zarcone-Gloris).zip', 'Waterloo.1911', '02', 'Welly.le.Petit', 'zip'],
    # another rare number
    ['Tif et Tondu - 026#045 - Le Gouffre Interdit.zip', 'Tif.et.Tondu', '026', 'Le.Gouffre.Interdit', 'zip'],
    # HS syntax
    ['Valerian THS1 - Par Les Chemins De L Espace.cbr', 'Valerian', 'HS1', 'Par.les.Chemins.de.l.Espace', 'cbr'],
    # HS syntax variant
    ['Valerian THS 01 - Par Les Chemins De L Espace.cbr', 'Valerian', 'HS01', 'Par.les.Chemins.de.l.Espace', 'cbr'],
    # double numbers
    ['Secrets Bancaires - T01 - Les Associes 11    (1920).cbr', 'Secrets.Bancaires', '01', 'Les.Associes.11', 'cbr'],
    # everything can append
    ['Serenity.Firefly/01 - Serenity - Those Left Behind 1 of 3.cbr', 'Serenity', '01', 'Those.Left.Behind', 'cbr'],
    # no number special case, failed but OK
    # ['Free Scott Pilgrim (FCBD) (2006).cbz', 'Free.Scott.Pilgrim', '', '2006', 'cbz'],
    # strip bdfr different forms
    ['[BD Fr] BD.FR.-.Disparitions.-.02.-.Retour.aux.sources.II.-.(Mazeau-Ersel).cbr',
     'Disparitions', '02', 'Retour.aux.Sources.II', 'cbr'],
    ['[BD Fr] Agence Touristes - T01 - Voyages a la carte [1920].cbr', 'Agence.Touristes', '01', 'Voyages.a.la.Carte', 'cbr'],
    # variant of numbers
    ['Terres Lointaines V4 #4 (of 5) (2011).pdf', 'Terres.Lointaines', '4', '2011', 'pdf'],
]
datas_debug = [
    # strange naming but relatively common
    ['Le Mercenaire V9 #9 (of 13) (1997).pdf ', 'Le.Mercenaire', '9', '1997', 'pdf'],
    # inversion in title
    ['[BD-FR] - Sang des Porphyre (Le) - 01 - Soizic.rar', 'Le.Sang.des.Porphyre', '01', 'Soizic', 'rar'],
    # repetition of number
    #['4 Les Champs d\'Azur - 04 - Sarabande a la turque - (Giroud-Brahy) - [2560].cbr', 'Les.Champs.d.Azur', '04',
    # 'Sarabande.a.la.Turque', 'cbr'],
    # repetition of () ()
    #['Supercrooks 04 (of 04) (2012) (2048px) (theProletariat-Novus-HD).cbr', 'Supercrooks', '04', '2012', 'cbr']
]
datas_next = [
    #
    ['', '', '', '', ''],
    ['', '', '', '', ''],
    # ['', '', '', '', ''],
    # last
    ['ok_12_ok.pdf',              'Ok',      '12', 'Ok',    'pdf']
]


class NormalizeTests(unittest.TestCase):
    """ testsuite via examples """

    def setUp(self):
        bdnorm.opts = bdnorm.opts_parser.parse_args(['dir'])
        bdnorm.opts.debug = True

    def _run(self, expected):
        """
        check that parsed parts are equals to validated results

        expected[0] is the full  name
        expected[1] is expected serie
        expected[2] is expected number
        expected[3] is expected title
        expected[4] is expected suffix

        computed[0] is empty
        computed[1] is extracted serie
        computed[2] is extracted number
        computed[3] is extracted title
        computed[4] is extracted suffix
        """
        computed = bdnorm.normalize_file(expected[0])
        # check series
        self.assertEqual(expected[1], computed[1])
        # check number
        self.assertEqual(expected[2], computed[2])
        # check title
        self.assertEqual(expected[3], computed[3])
        # check suffix
        self.assertEqual(expected[4], computed[4])
        # +1
        return True

    def _run_all(self, datas):
        """
        run all test
        """
        nb = 0
        nbok = 0
        for t in datas:
            nb = nb + 1
            if self._run(t):
                nbok = nbok + 1
        print(('{:d}/{:d} {:2.0f}% correct'.format(nbok, nb, float(nbok)/nb*100.0)))

    def est_base(self):
        self._run_all(datas_base)

    def est_without_series(self):
        self._run_all(datas_without_series)

    def est_real_life(self):
        self._run_all(datas_real_life)

    def test_debug(self):
        self._run_all(datas_debug)


if __name__ == '__main__':
    unittest.main()
