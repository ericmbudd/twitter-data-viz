from flask import Flask
#!/usr/bin/python2.4

'''Programatically create lists or follow accounts'''

__author__ = 'ericbudd@gmail.com'

import getopt
import os
import sys
import tweepy
import inputapi
from time import sleep



USAGE = '''Usage: tweet [options] message

  Programatically create lists or follow accounts.

  Options:

    -h --help : print this help
    --consumer-key : the twitter consumer key
    --consumer-secret : the twitter consumer secret
    --access-key : the twitter access token key
    --access-secret : the twitter access token secret
    --encoding : the character set encoding used in input strings, e.g. "utf-8". [optional]

  Documentation:

  If either of the command line flags are not present, the environment
  variables TWEETUSERNAME and TWEETPASSWORD will then be checked for your
  consumer_key or consumer_secret, respectively.

  If neither the command line flags nor the enviroment variables are
  present, the .tweetrc file, if it exists, can be used to set the
  default consumer_key and consumer_secret.  The file should contain the
  following three lines, replacing *consumer_key* with your consumer key, and
  *consumer_secret* with your consumer secret:

  A skeletal .tweetrc file:

    [Tweet]
    consumer_key: *consumer_key*
    consumer_secret: *consumer_password*
    access_key: *access_key*
    access_secret: *access_password*

'''

listoflists = []
tempList = []
tempListNoDupes = []
followingList = []
whichLists = []

def PrintUsageAndExit():
 # print USAGE
  sys.exit(2)

def GetConsumerKeyEnv():
  return os.environ.get("TWEETUSERNAME", None)

def GetConsumerSecretEnv():
  return os.environ.get("TWEETPASSWORD", None)

def GetAccessKeyEnv():
  return os.environ.get("TWEETACCESSKEY", None)

def GetAccessSecretEnv():
  return os.environ.get("TWEETACCESSSECRET", None)

class TweetRc(object):
  def __init__(self):
    self._config = None

  def GetConsumerKey(self):
    return self._GetOption('consumer_key')

  def GetConsumerSecret(self):
    return self._GetOption('consumer_secret')

  def GetAccessKey(self):
    return self._GetOption('access_key')

  def GetAccessSecret(self):
    return self._GetOption('access_secret')

  def _GetOption(self, option):
    try:
      return self._GetConfig().get('Tweet', option)
    except:
      return None

  def _GetConfig(self):
    if not self._config:
   #   self._config = ConfigParser.ConfigParser()
      self._config.read(os.path.expanduser('~PycharmProjects/TimelineFilter/.tweetrc'))
      print(os.path.expanduser('~/PycharmProjects/TimelineFilter/.tweetrc'))
    return self._config

def rateLimitChecks(api):

  ratelimit = api.rate_limit_status(resources='friends')
  print(ratelimit)

  ratelimit = api.rate_limit_status(resources='lists')

  print('/lists/list calls remaining = ' + str(ratelimit['resources']['lists']['/lists/list']['remaining']))
  print(ratelimit)

  if ratelimit['resources']['lists']['/lists/list']['remaining'] < 1:
    sys.exit("API limit reached")


def createNewList(api):
  #gives the user the option to create a new list before adding members to list
  global tempListNoDupes, listoflists

  createList = input('Create new list? (y/n) = ')

  if createList == 'y':
    newListName = input('List name? = ')
    api.create_list(name=newListName,
                    mode="private")

    listoflists = api.lists_all (
                     screen_name='ericmbudd',
                     user_id=None,
                     reverse=False)


    for b, i in enumerate(listoflists):
      intb = int(b)
      print(b + 1, listoflists[b].name + ' ' + str(listoflists[b].member_count))





def getListsInfo(api):
  #display list of lists for a user

  global whichLists, listoflists
  listoflists = api.lists_all (
                   screen_name='ericmbudd',
                   user_id=None,
                   reverse=False)

  #following is separate from lists and handled differently
  print("0 Following " + str(listoflists[0].user.friends_count))
  print(listoflists[0])

#  print (listoflists)

  for b, i in enumerate(listoflists):
    #print listoflists[b]
    intb = int(b)
    print(b + 1, listoflists[b].name + ' ' + str(listoflists[b].member_count))

  print( '')

  whichLists = input('Enter list numbers to use (comma delimited) = ').split(',')

  print('')

  totalListMembers = 0

  for i in whichLists:
    inti = int(i)

    if inti == 0:
      totalListMembers += listoflists[0].user.friends_count
      print("Following " + str(listoflists[0].user.friends_count))
    else:
      totalListMembers += listoflists[inti-1].member_count
      print(listoflists[inti-1].name + ' ' + str(listoflists[inti-1].member_count))

  print('')
  print('totalListMembers before = ' + str(totalListMembers))


def processListMembers(api):
  global tempList, listoflists, tempListNoDupes


  #cycle through list of lists (as selected by user)
  for i in whichLists:
    inti = int(i)

    #handle following (not a list)
    if inti == 0:
      print ("inti == 0")
      members = api.followers_ids(
        owner_screen_name="ericmbudd",
        cursor=-1)
    #    count=5)
      print (members)
      #cycle through members of each list
      for a in members:
        for b in a:
          if b == 0:
            break
          try:
            if inti == 0:
              tempList.append(b)
              print (b.id)
            else:
              tempList.append(b.id)
              print (b.id)

          except:
            continue

    else:
      print ("else")
      #default -1; 0 = list done
      cursorTracker = -1
      while cursorTracker != 0:
        members = api.list_members(
          list_id=listoflists[inti-1].id,
          slug=listoflists[inti-1].slug,
          owner_id=None,
          owner_screen_name='ericmbudd',
          cursor=cursorTracker,
          count=500)

        cursorTracker = 0


        for a in members[1]:
          if a > 0:
            cursorTracker = a
     #       print cursorTracker

        for a in members:
          for b in a:
            if b == 0:
              break
            try:
              if inti == 0:
                tempList.append(b)
                #print (b.name)
                print (b.screen_name + "| ")
              else:
                tempList.append(b.id)
                #print (b.id)
                #print(b.name)
                print (b.screen_name)
                print (b.id)
                #print (b.following)

            except:
              continue

        #print(len(tempList))

    #print(members)

  #used for all final list/follow processing
  tempListNoDupes = list(set(tempList))

  print('totalListMembers after    = ' + str(len(tempList)))
  print('totalListMembers after ND = ' + str(len(tempListNoDupes)))


def followAccountsOrPopulateList(api):
  global tempListNoDupes, listoflists, followingList

  listToFollow = []

  addAccountsToList = input('Add Accounts To List? (y/n) = ')
  followAccounts = input('Follow Accounts? (y/n) = ')

  #print(tempList)

  if addAccountsToList == 'y':
    #add members to lists in increments to prevent API squashing
    listIncrement = 100
    listRangeStart = 0
    listRangeEnd = 0

    #give option to create new list before adding accounts to list
    createNewList(api)

    # manual entry
  #  tempListNoDupes = ['funkykomadina',  'krstnbrkhldr',  'CPBaron',  'MoreyB',  'Boulder_Lady',  'TrinityOutside',  'zinnemily',  'Ken_Far',  'bracken',  'Cat_Wilfong',  'sseagraves',  'NathanLubchenco',  'mikegehard',  'vbettyincid',  'seatonlauren',  'CoffeeTalkMom',  'DaveDrach',  'coryshaw',  'wattsski',  'marie_willson',  'corinnarobbins',  'douggilkey',  'bandelier',  'RealLisaCSmith',  'KristinaStamat1',  'placesmakeppl',  'trackingteton',  'JustSegall',  'denaliimpact',  'msanclem',  'gwinterequinox',  'NHaasPT',  'wendyverse',  'rrowlandco',  'brycewidom',  'hollywsprague',  'heathralda',  'steveouting',  'ShowUpMatt',  'meganquinnnn',  'ed_narvaez',  'ScottTietzel',  'BANDmate_HEY_O',  'sacthe6',  'JustinBall01',  'lauraloveslux',  'tomkingsford',  'erikalogie',  'agahran',  'DarrenDeReuck',  'bldrgal',  'DanDeGolier',  'rogerpielkejr',  'sugardesigninc',  'JSherard',  'espinozaa',  'camberleyb',  'MyHomeinBoulder',  'scottholton',  'WideEyez',  'bruceschoenfeld',  'DavidAbelson',  'BoxStrategy',  'RivvyNeshama',  'sallykeefe',  'rhymeswithmilk',  '23mwalsh',  'johnnymolasses',  'alan_townsend',  'webber_pete',  'dalestetina',  'mikebrouse',  'Dan_In_Boulder',  'CwPearce',  'BenitaADuran',  'bigman718',  'juliannajarabak',  'PaulVis186',  'helzapoppen',  'deanpajevic',  'kathygard',  'tiernanz',  'betsmartens',  'meta_d',  'mcowlz',  'BobbyStuckeyMS',  'bobyatesboulder',  'arinewman',  'DavidPenzkover',  'Nicholas_Flores',  'mewmewmew13',  'kristamarks',  'ninaend',  'ToddRunestad',  'ReginaCowles',  'mike211hart',  'rudymiick',  'einterview',  'lakmoller',  'mwood',  'sharoninboulder',  'PChis51',  'TayGuay99',  'wcadkins',  '1daPC',  'ArtRoberts5',  'matt_ice',  'AntelopeBeads',  'BelknapJoanne',  'lomay1984',  'Kris10BrownPhD',  'gtuerk',  'PQBoulder',  'LesleyBoulder',  'jencasson',  'WillToor',  'rajatabhargava',  'DonniePee',  'chrisgrealish',  'benjamin_smith',  'garyiles',  'SteveFenberg',  'drawohara',  'brianmetzler',  'RustyMcCoy1',  'billcarroll',  'MercuryThe',  'michaellovato',  'odarren1',  'TeddyWeverka',  'toddreedjewelry',  'askwpgirl',  'hollierogin',  'wanek',  'ejoep',  'bobmorehouse',  'bhalsey',  'trufuel',  'andyschult',  'mpacocha',  'alkaitis',  'LizinBoulder',  'slartinyc',  'matbarlow',  'EcoBuildInc',  'tommyvee22',  'nicklegan',  'waylonlewis',  'Thomasacquinas',  'JRoth',  'Anuniaq',  'CindyMarvell',  'debrajason',  'KenOatman',  'denco83',  'Cindy4Council',  'kuczun',  'ClaireWalter',  'jimfranklin',  'RachelClaireHay',  'brettrjackson',  'mtnbikechic',  'Atianne',  'pauladupre',  'shellymboulder',  'Alquemiestudio',  'MikeDorsey6224',  'Kaitlin_Ko',  'amy_clark1',  'BLHarding99',  'JamesOClark',  'chefannc',  'edbyrneboulder',  'bryanlbowen',  'stevehath',  'shankargallery',  'RichardValenty',  'buffs4life2',  'lizjmeyer',  'cherryboulder',  'AlanOHashi',  'davedtowle',  'jungledave',  'DirkFriel',  'TMueh',  'SageBHobbs',  'shawnsie',  'AaronBrockett12',  'TheCharlier',  'bltnow',  'suefoolery',  'chrisbellco',  'estrellaboulder',  'USFoodDude',  'fishnette',  'EdieHooton',  'cj_gauss',  'MicheleSMoses',  'ConorHeun',  'carlybrantz',  '2Lazy2Fail',  'sheets_fran',  'jtwinsor',  'KimberlyKidder1',  'actingupmama',  'JonesZan',  'Elise4BoCo',  'danfox',  'drakedd',  'gratzo',  'chrismoodycom',  'v6flatb3d',  'gracehood',  'nickwyman',  'stevejinclev',  'boulderhistory',  'landcruiser13',  'sdsparn',  'MikePlattCO',  'Colo_kea',  'sjelmes',  'Shoemaker4City',  'PhilipEGraves1',  'realdannyconroy',  'danstorch',  'JyotsnaRaj1951',  'scolby738',  'melhiker2',  'cosunshinemka',  'hillaryrosner',  'schoenieee',  'Shoemaker4CU',  'GilComMedia',  'bethhartman',  'NicoleDukeNow',  'jerryshapins',  'runcari',  'nedmcclain',  'martharoskowski',  'AdmireTheMeyer',  'cpm5280',  'hannahnordhaus',  'mattkelsch',  'pea53',  'patrickcameron',  'S_Allen_IIoT',  'NattyZ',  'teeparham',  'mpbahl',  'haandances',  'CJANasta',  'hillarygriffith',  'eight4eight',  'lauriealbright1',  'BoulderJeff',  'annb',  'carlottamast',  'Cinemynx',  'ElisaBosley',  'MichelleVancil',  'danielfeld',  'copiousfreetime',  'InnovateMoore',  'Sterner',  'kenhotard',  'BoulderGraf',  'doylealbee',  'odellconnie',  'jenthink',  'philliplarson',  'jamesfbarry',  'AlexLMedler',  'boulderrunner',  'winedunce',  'Jessicaghdz',  'thisbloominlife',  'boulderwiz',  'suestuller',  'MountainWave',  'scumola',  'seanhudson',  'BoulderLisaS',  'boulderscribe',  'nealhenderson',  'darkhorsetri',  'paulmigs',  'catnipp1',  'ArleneVicki',  'lairdhunt',  'limscoder',  'mizlizhanson',  'NoDougButDoug',  'elispat',  'Tayertweet',  'vernonluke',  'BoulderTayer',  'yellowspur',  'EEHuck',  'tashada',  'gwenergy',  'RepClaireLevy',  'KarenBernardi21',  'emilyinboulder',  'marclivolsi',  'AMurphias',  'jweiman',  'markgelband',  'jeffhoobler',  'ginambarajas',  'rdosser',  'oats23',  'Miss_Mandaline',  'Starkkitty18',  'dancemomjason',  'briantsuchiya',  'barbmaiberger',  'VimalaMcClure',  'jonny2dope',  'skifellows',  'symesgc',  'cheryl303',  'meloneer2003',  'marcsobel',  'CherylMarkel',  'SachaOnMoney',  'nealmcb',  'nataliemeisler',  'hackathorn',  'JanetLeap',  'willhenderson',  'suebutcher',  'mgalloy',  'CHIROPOLOS',  'jennifershrive2',  'dzacek',  'KenBoulder',  'massageboulder',  'KellyBearer',  'MorganLommele',  'ScottMoorhead',  'KennaBruner',  'rorykelly',  'chaspinrad',  'jennberg',  'andreagibson',  'EpsteinDaniel',  'nickpassanante',  'welnoan',  'amyrosenblum',  'rachelryle',  'tenor112',  'M_Friedbird',  'davidsecunda',  'dpricesp',  'mooreds',  'thelegendmaker',  'kcbecker',  'HippiemansPlan',  'inghamemerson',  'lmckeogh',  'Rumblinbuffalo',  'manifestcookies',  'BambiWineland',  '_johngifford',  'zvanderkooy',  'CrystalBoulder',  'arch11inc',  'Brendanemoran',  'robschuham',  'nealrogers',  'AndreaMeyer',  'jaredpolis',  'ztuylime',  'posiczko',  'TheRice',  'rodrigjc',  'bill_allen_21',  'mimstah',  'boulderbits',  'marydoloyoung',  'jives',  'ecovisionary',  'PaulAikenBDC',  'AllenKrughoff',  'AscendCoach',  'bethejensen',  'rideboulderco',  'tomkalinski',  'arisirenita',  'Aitoshi2',  'FasCat',  'chadmoore',  'palebluedotguy',  'ChefHosea',  'jenniferegbert',  'scot_corn',  'boulderfuzz',  'RkyMtnVogel',  'SLC_CO',  'PhilipTobias',  'jane_knows',  'DAGarnett',  'Papa_Whit',  'SaraCsit',  'LisaMHarris',  'johnwbradley',  'GregOnMoney',  'bouldersteve',  'jim_mapes',  'Brookaitken',  'derrelldurrett',  'JakeTimm',  'LisaMcAlister',  'mdpiper',  'JTBoulderHomes',  'julirew',  'joannazeiger',  'davidcohen',  'douglasjbrown',  'GeriMB',  'jefflesser',  'pberberian',  'Colleen108',  'digidigo',  'rogernicholsmd',  'camdyetri',  'AdamSchabtach',  'quiltfairy',  'GordonShannon',  'Anita5280',  'hoosteeno',  'joelindsey',  'lauraannguy',  'rontupa',  'danmclellan',  'FrankieBenning',  '_toriwebster',  'LDameron',  'denisemfranklin',  'June_LMoore',  'LaurieJess00',  'dhspesh',  'pkstrode',  'brzimmerman',  'dave_frick',  'ultimateboy',  'cairns',  'HealthinBoulder',  'janehummer',  'alireder',  'sonicgoddess',  'mdevery01',  'bxposed',  'bethjhayden',  'lentinealexis',  'karagoucher',  'YourWheeltor',  'mrtommywest',  'brookbhakti',  'jp_obrien',  'AmyRobertsOIA',  'sonyahausafus',  'sampweaver',  'RMartinBoulder',  'MattdeCaussin',  'Haislmaier',  'cweidner8',  'threatresearch',  'BlissfulJill',  'LeBeurre',  'johnny88keys',  'hsdiamond',  'Satchellriffic',  'kcbigring',  'blue_dominique',  'brentertz',  'susan_kemp',  'ktoltz',  'KPLegan',  'pdignan',  'dougastevens',  'kjonuska',  'farmsharesinfo',  'airjustin7',  'jgamet',  'trishgroom',  'downclimb',  'colorado_kim',  'twistedbob',  'juddnutting',  'wrightkindaguy',  'RogerWolsey',  'teamweissmann',  'kristiankerr',  'jooduh',  'zndx',  'ZaneSelvans',  'ObsidionStorm',  'Elaine',  'MegFretz',  'HeartofColorado',  'craigrandall',  'daimowrench',  'adventurerneil',  'jlebert',  'thedancondon',  'JessicaMorgan',  'lwidd',  'rdawkins22',  'sarahprotz',  'alterego',  'MikeyFriesen',  'summerlaws',  'kencairn',  'StrangeShadows',  'davisphinney',  'glennlieberman',  'zefhous',  'dbrown',  'MelissaColo',  'KThammond',  'KristenEStiles',  'bmacferrin',  'DennyMcCloskey',  'mattpat1',  'jenbeaupre',  'spino_powerlegs',  'AmyStarrAllen',  'bouldersmith',  'NoahFierer',  'mchipouras',  'tsdock',  'Gnurps',  'Boulder_Beth',  'ktstj',  'sueprant',  'MomVaughn',  'racheljowalker',  'danicap',  'timrohde',  'jennabuffaloe',  'AudienceDevSpec',  'alex_howes',  'aly_masch',  'alliehalla',  'DijitalBuddha',  'jasonmendelson',  'ahross1',  'LindsaySutula',  'epibuff',  'morganmc_co',  'MarieAdams366',  'boulderbliss',  'MtnRunner_ELee',  'DrFonoFile',  'wdsmeyer',  'heroinebook',  'pedalingcorn',  'brentdaily',  'petergenuardi',  'boguskyswife',  'bogusky',  'MarkyV',  'ben_delaney',  'nicanadian',  'sugaree303',  'philmcmichael',  'IMsoulcrusher',  '1ejfrankel',  'jillgrano',  'polyphany',  'r3ndl',  'RealAdamClayton',  'EllaPadenLevy',  'maxwoodmont',  'ErinMKummer',  'BoulderVal',  'RonicaRoth',  'bcarmic',  'lesliefreee',  'thmscwlls',  'mmcyclist',  'erineve_de',  'ErinWeed',  'schroy',  'pattykake84',  'mccoysg',  'piddonkadonk',  'rushtonm',  'ericmagnuson',  '_Freeskier',  'ashc0in',  'patrickrea',  'thepentzagon',  'JakeWells',  'CaitMisencik',  'scottpcrabtree',  'CarrieSimon',  'MarkSHarrison',  'AllTerrainRunnr',  'JohndComiskey',  'jefftmack33',  'flynnboulder',  'LawnParty',  'AmySegreti',  'markgammon',  'StvKas',  'beala',  'aimee_minard',  'ScottKiere',  'bobbymartines',  'KeciaBenvenuto',  'susaneverett',  'electromute',  'nico_valencia',  'billythekidtri',  'ash_haga',  'BoulderNigel',  'Richncook',  'Pegasas3030',  'kimbal',  'adeibold',  'lwhitcher',  'DonnyW',  'JoyRedstone',  'briafar',  'vickying',  'parkerbenson',  'JPedelty',  'CSutherlandS',  'jasonbikes',  'DaveMRich',  'melodyfairchild',  'nikkibot',  'jlgerweck',  'JeffHosBoss',  'DeanHurtt',  'PamMooreWriter',  'justinrezz',  'sierraksamuel',  'ForKidsSake',  'llennip19',  'earlatron',  'betyoumitchme',  'ericmbudd',  'davidleecass',  'dcwoodruff',  'mwgauss',  'HanLevine',  'dkvollmar',  'BryanDcolorado',  'kaoudis',  'carinreich',  'hardidu1996',  'whlteXbread',  'johntomasic',  'deathorglory80',  'OtisTaylorBand',  'laurachernikoff',  'GeneVGlass',  '3dpt',  'baritessler',  'bkuhlmann',  'BobBaskerville',  'jaycrain',  'menro',  'jschwager',  'zacmitchell',  'Feeneyapolis',  'MartinNuss1',  'AmphibiYann',  'odog',  'WaypointFilms',  'jacobsonic',  'BeccaRobs',  'aMichaelCody',  'bracyknight',  'bwagert',  'ClarkRider',  'Whizardly',  'billyzacsmith',  'juliankyer',  'jamie_jezebel',  'ChristianMMacy',  'seavox',  'sarahchansonart',  'JasonSperling',  'cash4goldfish',  'lkbhas',  'JennyCpon',  'John_Snelson',  'head2bold',  'jserface',  'HollyHamann',  'HarrySurden',  'vikasreddy',  '144Megs',  'trackjenny',  'tmoshea',  'ryanwanger',  'abimickey',  'CarterJones89',  'JordanrMann',  'BoulderJeremy',  'cookrn',  'admiraljonjon',  'cmgosnell',  'Rustickles',  'ABridenhagen',  'joshwiner',  'mherringart',  'ScottJonker',  'InaRealCO',  '2morethings',  'tygern',  'narancis',  'phongybutt',  'jesstri4fun',  'CaleyFretz',  'vanessacarmean',  'BoulderStefanie',  'TeachLearnLive',  'matthewlcooke',  'prindlescott',  'sefeuerstein',  'willnabours',  'mudandcowbells',  'taylorphinney',  'jhurd',  'skibikeglitter',  'Kacyyy',  'BenRobertson',  'amandamarkert',  'FreckldByTheSun',  'gwaki',  'chelseaflagg',  'karen_kosiba',  'sjboulder',  'tylerjwils22',  'ZaneZirschky',  'boykoff',  'awnowlin',  'brianthefirle',  'chelseansays',  'CornerstoneFarm',  '0xCOLIN',  'whitneyrogers',  'gregibrown',  'jeffoeth',  'ophelea23',  'AnthonyClaudia',  'tonirosati',  'timestanley',  'janburtonco',  'nickparsons',  'charles',  'walkablestreets',  'PhotoLesa',  'jrwiener_1980',  'Gaard',  'austindufault33',  'LauraRBennett',  'jon_cardwell',  'tahoe1966',  'JennaBeeYoga',  'Flattop8',  'eatullis',  'ericdconrad',  'willhauptman',  'rmontonio',  '_SeanOBrien_',  'JFrank32',  'BobGordon',  'fletchrichman',  'aaronagray',  'LucasHayas',  'MichaelKodas',  'jagolinzer',  'habibwicks',  'chelseaejewell',  'austereapril',  'david_glover',  'royer_alejandr0',  'flyestladyj',  'andrewlr_',  'reubenmunger',  'woodardj',  'Citizenvelo',  'DataRiot',  'mindfulplay',  'PalsyWalsyD',  'maesto',  'SeaCee8',  'ideavist',  'snowforecaster',  'laurarich',  'EngRecruitRecur',  'JessiBraverman',  'andrewhomeyer',  'cshank27',  'emmajcoburn',  'codeangler',  'HeatherMargolis',  'yoavlurie',  'AmandaGrennell',  'alanawlsn',  'bpenuel',  'IAmGriffinKay',  'sellout',  'mrandyclark',  'ScottJurek',  'MrFasthorse',  'ValerieGoren',  'rachelv',  'FutureofWomen',  'offyonder',  'rwpeterson',  'Stormspandies',  'LukePatrick',  'LindsaySandoval',  'SandovalEmily',  'AaronEkalo',  'bike',  'mikeabiezzi',  'ratherironic',  'Katie_Dunn',  'JaimeeHoefert',  'threeseepeeyo',  'reenarooks',  'iankuliasha',  'LaurenGifford',  'dianam',  'kkurian',  'sa_katz',  'TheOptimistCo',  'tatmaxwell',  'InfiniteWeeknd',  'jberd',  'MindOfMelanie',  'cgenevier',  'veryblair',  'TIGilboa',  'matsteinmetz',  'timmayer',  'christinelcody',  'andrewzimmer906',  'andrewskurka',  'BrendanBenson',  'ericgalenyoung',  'itsalexcampbell',  'whitneyljames',  'bigbroncosfan',  'BeauGamble14',  'PKPostmansKnock',  'hrdavis1',  'ericaogrady',  'bikepedbrian',  'Jeanne_EE',  'joyfulsolutions',  'walterbreakell',  'SpencerCarnes1',  'userbeau',  'LynnYarmey',  'notFromShrek',  'ltrifon',  'Frederic_Terral',  'PureCunningham',  'julijellybean',  'ashleyfarringt2',  'DenaliHussin',  'kennettpeterson',  'stvdln',  'SEBMarketing',  'aloumey',  'CraigASchiller',  'adnroy',  'MisterKerwin',  'eezis',  'DrDesmo',  'joepolman',  'CalliePederson',  'DaveTelf',  'lucaseuser',  'nathansobo',  'jacksonfox',  'JennaBlumenfeld',  'MorganRehnberg',  'suzannahsterten',  'LeahAWasser',  'DaneDeLozier',  'axk',  'underwrite_88_5',  'HuanWin',  'iammattnull',  'evegodat',  'CorbGrant',  'jallison94',  'kamterbeek',  'michaelamujica',  'SamGastro',  'shayshinecastle',  'ericwryan',  'emilysalas',  'MikeOz_',  'analiesemarie',  'chucklief',  'andrewraphael',  'J_Noons',  'ArieannD',  'HelloAlexGarcia',  'ConnorWDavis',  'jakehurysz',  'Stepan',  'kenford',  'alexeydavies',  'CaitlinRockett',  'davidhekman',  'tellsue',  'Kai_Casey',  'DrRichardHansen',  'thomaswoodson',  'bryanalders',  'AstroCook',  'shawnnamullenax',  'evan_bernier',  'crosbycj',  'perella',  'dopplershift',  'samntx',  'sandramchung',  'AlastairTheScot',  'icesar',  'JamesNSherwood',  'TheSeanBrady',  'GR_G_R',  'jefferyjake',  'mmehnert1',  'NateThaGr8t99',  'LTDaanIceCream',  'genfixie',  'SageCanaday',  'lifeofleonardo',  'wjrigler',  'gayledoud',  'Aric_vh',  'cevaris',  'LeftistConnor',  'robineckmann',  'toby_hammer',  'ShalayaKipp',  'aegeorge4',  'CwaDrums',  'Heathbar721',  'ZacBarger',  'GregGoodson',  'SamKlomhaus',  'dr_lunch',  'kellytwigger',  'wuddupdok',  'ColinWichman',  'mathewsisson',  'zackkanter',  'bricktuh',  'SJAdams',  'brvndonbver',  'marshallphayes',  'bentremper',  'ebeewest',  'EEversbusch',  'CUCoachElliott',  'AlecAstrochem',  'kayladanea50',  'DivorceBusting',  'JulianaMcCarthy',  'forneverlost',  'Ambii_anne',  'agnellvj',  'mattcheston',  'Nickeldm',  'MissNattyP',  'ttotemeier',  'johnweiss',  'DaContentKing',  'CSajet',  'rylanb',  'shannonrcarlin',  'jde66leston',  'johnfdennison',  'JLBornstein',  'CAlvarezAranyos',  'lukeinusa',  'erinlpc',  'GregBennett1',  'JimPeterman',  'dreampinkus',  'p5k6',  'ORourkeCM',  'the_real_mags',  'tshade42',  'GeoBigData',  'rsoden',  '8tefan',  'dalmasha',  'whitneymriker',  'M5Hansen',  'stephbachman',  'PopePolar',  'unidata_josh',  'cydtanner',  'BryanBakke',  'EmSheridan13',  'ArchaeoHacker',  'RaffiMercuri',  'saraisnyder',  'AmazinKazin',  'karinicolaisen',  'JordynKTVZ',  'ericakuhl',  'Kreagz',  'crabbyabz',  'NoahSchultz7',  'nickromeo24',  'josephrkasprzyk',  'mcclurmc',  'ncayou',  'khaledcallen',  'hydewright',  'MrPresidentMatt',  'JanineADolan',  'joncbates',  'BatesSara',  'amiruhhh',  'gavthemechanic',  'iamnader',  'birsic',  'westonplatter',  'RickGeorgeCU',  'bryanmuir',  'pcv2000',  'frEidem_Fries',  'nottil',  'micah_frost',  'DougTI',  'cutiger5580',  'LizKONeill',  'hansfertig',  'sarabeand',  'David_MSullivan',  'Saraekingsley',  'Derek_Zahler',  'michaelshahamat',  'hunterwriterer',  'Dean426Dean',  'andrewbaron',  'YarrowLinden',  'sritchie',  'adam_mayer',  'athousandjoels',  'higginsk8',  'tobinkaestner',  'katlynbjohnson',  'WDCChick',  'PatrickDFischer',  'MaryRkelly',  'bpb01909',  'tomblue',  'TonyTarbox',  'MAJungclaus',  'amherman',  'EricaVanSteenis',  'spencerhaddy',  'Rogencrans',  'BatDorn',  'maddietaber',  'sbrown',  'gingerbtweets',  'annie_catterall',  'murraymeetze',  'kubakostecki',  'graugustine',  'GrossMaddie',  'hilljb',  'pamelanurrie',  'TheGhostofMarv',  'bminortx',  'WhitneyWuphf',  'lindsey_loberg',  'kristin_rey',  'Tsmendoza',  'maxx_chance',  'nicole_b_ryan',  'Mrmattjens',  'meghanmacdeezy',  'BrandonTuley53',  'maldonadoowen',  'shaunkane',  'PatrickVanHorne',  'DimitriNakassis',  'asiankarljwolf',  'peNELLope7',  'coreykohn',  'boulderbob',  'CSNBean',  'KassondraCloos',  'jaimerothlaw',  'LisaVanHorne31',  'meowIItsdianne',  'kaitlynbunker27',  'brittenwolf',  'XXfounder',  'Jerbivore',  'Andrewphilipfre',  'DBergholz',  'alisha_baca',  'annabelbonner',  'goodLifeEats',  'vmazal',  'sarahtoil',  'alex_burness',  'rafitaffyrahman',  'mmillller',  '_jadebegay',  'tranquilotravel',  'jdegoes',  'djspiewak',  'TreebarkMark',  'dizzvh',  'paulwallick',  'Aff4T',  'noahgranigan',  'elemdoubleu',  'yolayne',  'bWEB',  'ChaseKregor',  'EJBeans',  'TheHungry_Hippo',  'mtwist333',  '_chrishaynes',  '_Jack_F',  'djkz',  'ChrisAnthony_G',  'ZimmermanTrevor',  'Bart_Foster',  'abbysbenson',  'christianteehee',  'eamillikin',  'MBerger47',  'NicBoerio',  'stephoneil',  'AileenCarrigan',  'at_plhjr',  'ericswanson',  'boulderwild',  'sabrinamcgrail',  'AllysonDowney',  'juliebeanb',  'LesleySmithTri',  'get_kare',  'A_MillerDesigns',  'sam_caylor',  'bmurple',  'BenKyster',  'DanielleEck',  'smileitsshanna',  'JeremiahOsGo',  'AlsoColor',  'thinkjc',  'striphas',  'PhaedraPezzullo',  'MarilynSRogers',  'DanEvans108',  'lucyccheadle',  'Evan_W24',  'kylefrost',  'RJoyce09',  'gray8110',  'universeclock',  'bescka',  'Dfeeney31',  'Alex_Parker',  'BlissnHarmonyTP',  'smyjewski',  'english_teach79',  'halleezz',  'BairdAdin',  'PhilipGarcia15',  'AusendaGiorgio',  'sophia_c19',  'DaveTaylor',  '_caresmith',  'StevenDilla',  'durableham59',  'KarissaKloss',  'nicolehering',  'ESIP_Erin',  'RealMatSmith',  'kristinjswisher',  'chlsrgrs',  'jayssface',  'boonrs',  'MattScience',  'BrianneAllan',  'GretaSeidohl',  'TheRealJayGreco',  'laur_ash427',  'AscendingNode',  'DougInBoulder',  'ForTheHealth',  'Breen_Katie',  'soulswirl',  'caelanthom',  'sage_korin_yw',  'StevenFrost',  'twit_koda',  'local_cal',  'maryannerodis',  'mmaiorino',  'martin_yoselin',  'PedrovonSimson',  'Hegemommy',  'bfenton23',  'terencehiggins',  'SydneyHofferth',  '_tswilson',  'ajgreenfeld',  'seegizmotweet',  'j_hines4',  'ricktrilsch',  'chrisnelder',  'DanielleDannen',  'AnneLindley',  'rmulley',  'karinaxroberts',  'RebMarc',  'SabraBerger',  'johnbearwithme',  'Steadmils',  'LaurynRatashak4',  'Caroline_Early',  'HoolianSmith',  'angel4impact',  'Brittanylane515',  'alexfinnarn',  'ninarome29',  'chrisbrewer62',  'mjp39',  'KPWhite330',  'MattGiovanisci',  'potterjohnr1',  'dbseaton',  'toddmoy',  'adamdill',  'tonybgoode',  'KyleEstrada28',  'stareinthebeard',  'b_hans1520',  'JHurwitz16',  'zwartns',  'yuffieh_',  'jzimmerman20',  'davetamkin',  'zehra_cheatham',  'nickcotephoto',  'MTzimourakas',  'Jam_sCh10',  'erlinden',  'orianarichmond',  'jjjjustin',  'joshwolff',  'Kate_Catlin',  'ELexplore',  'zmillr',  'bychasehowell',  'nikkidhodgson',  'lisamunro22',  'neilxnguyen',  'mincic92',  'KASully16',  'shayepalagi',  'libraryfemme',  'seancllns',  'craiglewis85',  'seanhelvey',  'tm_hopp',  'RealLiveNicole',  'StephHalligan',  'JeffLupinski',  'kellyshalk',  'DeanEberhardt',  'nickthewalsh',  'KikiSkinner',  'erinoutdoors',  'bkeegan',  'alexamorey',  'kathyschultz22',  'bthompson4119',  'ziggyzarvatine',  'AustinOnSocial',  'WilliamKorn15',  'NicholasMonck',  'MarcusPadmore',  'jacks7596',  'Jolarson12',  'SDACapeBreton',  'VSmelk0_II',  'EllaRasmuson',  'marinavance',  'rarinald',  'CoreyLBuhay',  'heyyhayhayley',  'raelnb',  'jakedahn',  'ntnsndr',  'KirstenRowell',  'ervance',  'JeneuseG',  'robjohnson',  'afbillings',  'brianclark',  'emmagramirez',  'gegere',  'Zacharycohen',  'dgrnbrg',  'reillymcgavern',  'MsDan1elleBrown',  'JoshMalashock',  'natashairizarry',  'JakeMcClory',  'LindseyDanforth',  'keighleeriggan',  'quesinberry3827',  'emily_krough',  'uplightblog',  'xlerb',  'maddiecupchak',  'vtapia',  'AdamJonez',  'swartretort',  'spyyddir',  'dschobel',  'shwizzyyy',  'lacymckenny',  'errcaderk',  'PigottAsh',  'cneuhring56',  'grace_elizz',  'jsrothenberg',  'mike_hammes_3',  'reneemariee__',  'heidwee',  'MissAerospace',  'Lauren_Clarice',  'loganhaak_',  'ChynaSlade',  'RockyMntRaiderX',  'JRob_0',  'shaunlysen',  'brooklyn_saeman',  'chrisjvargo',  'SamBamZwirko',  'elenadulys',  'brittanyreddy',  'jenrunsworld',  'patrickryan',  'ryan_go_gomez',  'traveladvising',  'S_Henderson_',  'evilspinmeister',  'miranda_vigil',  'cambab44',  'shiflett',  'jdzumba',  'marinaro_frank',  'SaraRecruit4U',  'DFried615',  'twolowicz24',  'baylee_sergent',  'frederickcook',  'SingletrackZach',  'Lofo44',  'fbeckwith',  'kanadawomaninus',  'AbigailWise',  'agalex12',  'MichaelCarcaise',  'BillKlimczakJr',  'mikecappsdotcom',  'lachlanmp',  'SidneyBushman',  'YouLoveTacoBell',  'BonnieLBlocker',  'pauljmcr',  'tskaggs',  'riley_schmitz',  'jbavari',  'ajkahny11',  'TroyConant',  'xoxoashliroo',  'evysallinger',  'jaronurban',  'sarahgarney',  'theCourtneyO',  'lizinauth',  'NancyInghamm',  'dhylbert',  'viokylelinn',  'caitlin_lam',  'LeoFosterGreer',  'Clark_w8',  'MikeOffTheMap',  'krupey',  'adamstpierre', ] #used for manual entry

    #print (tempListNoDupes)
    #process list in increments
    while listRangeEnd < len(tempListNoDupes):
        if listRangeEnd + listIncrement >= len(tempListNoDupes):
          listRangeEnd = len(tempListNoDupes)
        else:
          listRangeEnd += listIncrement

        print(str(listRangeStart + 1) + " " + str(listRangeEnd))

        #twitter API requires list ID and user ID to add to lists
        try:
          members = api.add_list_members(
            owner_screen_name='ericmbudd',
            slug='city-of-boulder-voters',
            #list_id=799799451783143424,
            #list_id=listoflists[0].id,
            #user_id=17937100
            #user_id=tempListNoDupes[listRangeStart + 1:listRangeEnd]
            screen_name=tempListNoDupes[listRangeStart:listRangeEnd]
          )

        except:
          print(tweepy.error.TweepError.reason)
          #print(api.)





        #update list tracker
        listRangeStart += listIncrement

  if followAccounts == 'y':
    # add twitter follower

    #get current list of 'following' from account
    followingList = api.friends_ids(
    owner_screen_name="ericmbudd",
    cursor=-1)

    #subtract accounts already followed from the 'big list' to follow
    listToFollow = list(set(tempListNoDupes) - set(followingList[0]))
    #listToFollow = list(set(tempListNoDupes))

    #listToFollow = [] # used for manual input
    listToFollow = [

14659182,
4291135400,
76685457,
80361522,
81217377,
887241948,
3948497533,
33456685,
107115131,
34357873,
23375994,
1104903222,
111682436,
27771942,
412473645,
14819514,
16227384,
1729664714,
392469241,
3077980326,
108213264,
637256026,
114336396,
382313051,
220283656,
211628825,
81893043,
731882971825741824,
17238095,
1963594830,
321492572,
85584384,
4769466625,
8025882,
9744232,
2335752644,
7739832,
14355142,
10447232,
151083037,
301647849,
81867128,
14771728,
14473778,
47858209,
22399212,
16033525,
24002284,
466880049,
37088530,
37855357,
14311703,
358375670,
22375725,
72644699,
1964876576,
411180066,
13483732,
14182218,
1493923903, ] #used for manual entry


    print('tempListNoDupes = ' + str(len(tempListNoDupes)))
    print('followingList = ' + str(len(followingList[0])))
    print('listToFollow = ' + str(len(listToFollow)))


 #   listToFollow = [  64751203, ] #used for manual entry
    #print(listToFollow)

    followCount = 200
    #if (len(listToFollow) < followCount):
    # followCount = len(listToFollow)

    #follow, just new accounts

    '''
    for a in listToFollow:
         members = api.create_friendship(
          user_id=a
          )
    '''


    for a in range(0,followCount):
      try:
         members = api.destroy_friendship(id=listToFollow[a])   #  (screen_name=listToFollow[a])
         print (listToFollow[a])

          #make user_id again, not screen_name
   #      screen_name=listToFollow[a]  #make user_id again, not screen_name

      except tweepy.error.TweepError:
        try:
          print(tweepy.error.TweepError.reason )
        except:
          print(tweepy.error.TweepError.reason )
          continue
        continue

      sleep(30) # Time in seconds.



def main():
  try:
    shortflags = 'h'
    longflags = ['help', 'consumer-key=', 'consumer-secret=',
                 'access-key=', 'access-secret=', 'encoding=']
    opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)
  except getopt.GetoptError:
    print('PrintUsageAndExit')
    PrintUsageAndExit()
  consumer_keyflag = None
  consumer_secretflag = None
  access_keyflag = None
  access_secretflag = None
  encoding = None
  for o, a in opts:
    if o in ("-h", "--help"):
      PrintUsageAndExit()
    if o in ("--consumer-key"):
      consumer_keyflag = a
    if o in ("--consumer-secret"):
      consumer_secretflag = a
    if o in ("--access-key"):
      access_keyflag = a
    if o in ("--access-secret"):
      access_secretflag = a
    if o in ("--encoding"):
      encoding = a
  message = ' '.join(args)
  #if not message:
  #  PrintUsageAndExit()
  #rc = TweetRc()

  print(consumer_keyflag)
  print(GetConsumerKeyEnv())
#  print rc.GetConsumerKey()



  '''
  consumer_key = consumer_keyflag or GetConsumerKeyEnv() or rc.GetConsumerKey()
  consumer_secret = consumer_secretflag or GetConsumerSecretEnv() or rc.GetConsumerSecret()
  access_key = access_keyflag or GetAccessKeyEnv() or rc.GetAccessKey()
  access_secret = access_secretflag or GetAccessSecretEnv() or rc.GetAccessSecret()
  '''



  if not inputapi.consumer_key or not inputapi.consumer_secret or not inputapi.access_token or not inputapi.access_token_secret:
    print('fail4')
    PrintUsageAndExit()

  api = tweepy.OAuthHandler(consumer_key=inputapi.consumer_key, consumer_secret=inputapi.consumer_secret)
  auth = tweepy.OAuthHandler(inputapi.consumer_key, inputapi.consumer_secret)
  auth.set_access_token(inputapi.access_token, inputapi.access_token_secret)




  api = tweepy.API(auth)

  rateLimitChecks(api)
  getListsInfo(api)
  processListMembers(api)
  followAccountsOrPopulateList(api)



####

#   except UnicodeDecodeError:
 #    print "Your message could not be encoded.  Perhaps it contains non-ASCII characters? "
 #    print "Try explicitly specifying the encoding with the --encoding flag"
 #    sys.exit(2)
  #print "%s just posted: %s" % (status.user.name, status.text)

if __name__ == "__main__":
  main()


@app.route("/")
def hello():
    return "Hello World!!"
